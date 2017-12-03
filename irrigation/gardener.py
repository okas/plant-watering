import logging
import os
import uuid
from contextlib import suppress
from datetime import datetime, timedelta
import queue
from threading import currentThread, Thread, Event, BoundedSemaphore
from unqlite import UnQLite
from .plant import Plant, State
from .water_supply import WaterSupply


log = logging.getLogger(__name__)


def add_seconds(s:float, format='%X') -> str:
    return (datetime.now() + timedelta(seconds=s)).strftime(format)


class Gardener:
    __watering_semaphore = BoundedSemaphore(value=1)

    def __init__(self, config):
        self.closed = False
        self.stop_event = Event()
        self.__db_worker_stop = Event()
        self.__worker_queue = queue.Queue()
        self.__db_queue = queue.Queue()
        self.watch_cycle = config.gardener_args.watch_cycle
        self.watering_cycle = config.gardener_args.watering_cycle
        self.plants = self.__init_plants(config.plants_args_list)
        self._db__id = None
        self.__db_thread = None
        self.db = self.__init_db(config)
        self.water_supply = WaterSupply(
            self.stop_event,
            config.pump_args._asdict(),
            (p.valve_pin for p in config.plants_args_list),
            config.tank_args._asdict()
            )
        self.__start_work_data()
        self.__start_work_watchers()

    def __del__(self):
        if not self.closed:
            self.stop_event.set()
            self.stop_event.set()
            self.close()

    def __init_plants(self, a_list) -> tuple:
        return tuple(Plant(self.stop_event, **a._asdict()) for a in a_list)

    def __init_db(self, config):
        if not (os.path.isabs(config.database_dir) and
                os.path.isdir(config.database_dir)):
            raise OSError("Expected existing and absolute directory "\
                          "path, instead of '%s'" % config.database_dir)
        db = UnQLite(os.path.join(config.database_dir, config.name+'.bson'))
        c_gardener = db.collection('gardener_instances')
        self.__db_moistures = db.collection('plant_moistures')
        self.__db_waterings = db.collection('plant_waterings')
        c_gardener.create()
        self.__db_moistures.create()
        self.__db_waterings.create()
        return db

    def __start_work_data(self):
        self._gardener_commiter()
        self.__db_thread = Thread(
            name = '_db_worker',
            target = self.db_worker
            )
        self.__db_thread.start()

    def __start_work_watchers(self):
        for plant in self.plants:
            self.__worker_queue.put(plant)
            Thread(
                name = "{}_watcher".format(plant.name),
                target = self.plant_watcher_worker
                ).start()
        log.info("Gardener is starting to watch for %d plants."\
            % len(self.plants))

    def db_worker(self):
        log.debug('Started database worker.')
        try:
            while not self.__db_worker_stop.is_set():
                with suppress(queue.Empty):
                    work = self.__db_queue.get(timeout=0.1)
                    func = work[0]
                    func(*work[1:])
        except:
            self.stop_event.set()
            log.exception(general_exc_msg)
        finally:
            self.db.close()
            log.debug('Completed database worker.')

    def _gardener_commiter(self):
        def extended_plants():
            for p in self.plants:
                p.uuid1 = uuid.uuid1()
                yield p
        gardener_record = {
            'uuid1': str(uuid.uuid1()),
            'watch_cycle': self.watch_cycle,
            'watering_cycle': self.watering_cycle,
            'plants':
                list({
                    'uuid1': str(p.uuid1),
                    'name': p.name,
                    'moist_level': p.moist_level
                    } for p in extended_plants()
                )}
        with self.db.transaction():
            self._db__id = self.db\
                .collection('gardener_instances')\
                .store(gardener_record)

    def _measure_commiter(self, p_uuid1, moist):
        with self.db.transaction():
            self.__db_moistures.store({
                'gardener__id': self._db__id,
                'plant_uuid1': str(p_uuid1),
                'ts_utc': datetime.utcnow().timestamp(),
                'percent': moist
                })

    def _water_commiter(self, p_uuid1, water):
        with self.db.transaction():
            self.__db_waterings.store({
                'gardener__id': self._db__id,
                'plant_uuid1': str(p_uuid1),
                'ts_utc': datetime.utcnow().timestamp(),
                'mil_lit': water
                })

    def _save_measure(self, p_uuid1, moist):
        self.__db_queue.put((self._measure_commiter, p_uuid1, moist))

    def _save_watering(self, p_uuid1, water):
        self.__db_queue.put((self._water_commiter, p_uuid1, water))

    def plant_watcher_worker(self):
        try:
            plant = self.__worker_queue.get()
            while not self.stop_event.is_set():
                moist = plant.measure()[1]
                self._save_measure(plant.uuid1, moist)
                if plant.state == State.needs_water:
                    log.info(" Enter watering cycle, moisture low: "\
                         "{:.2f}% (min {:.2f}%)."\
                            .format(moist, plant.moist_level))
                    self._handle_watering_cycle(plant)
                    if self.stop_event.is_set():
                        break
                    log.info(" returned to watch cycle, re-measure at %s."\
                        % add_seconds(self.watch_cycle))
                else:
                    log.info(" Enough moisture {:.2f}% (min {:.2f}%), "\
                        "re-measure at {}."\
                        .format(
                            moist,
                            plant.moist_level,
                            add_seconds(self.watch_cycle)
                        ))
                if self.stop_event.wait(self.watch_cycle):
                    log.debug(" stopping watcher cycle, because something asked.")
                    break
        except:
            self.stop_event.set()
            log.exception(general_exc_msg)
        finally:
            self.__worker_queue.task_done()
            log.debug(" completed plant watcher thread.")

    def _handle_watering_cycle(self, plant):
        '''Perform watering, measuring and re-watering if neccessary.'''
        while True:
            if not self._wait_for_tank():
                log.debug(" stopping watering cycle, because something asked.")
                break
            log.debug("  start watering.")
            actual_ml = self._water_plant(plant)
            self._save_watering(plant.uuid1, actual_ml)
            log.info("  re-measure moisture at %s."
                % add_seconds(self.watering_cycle))
            if self.stop_event.wait(self.watering_cycle):
                log.debug(" stopping watering cycle, because something asked.")
                break
            measure, moist = plant.measure()
            self._save_measure(plant.uuid1, moist)
            if not measure:
                log.info(" plant reached moisture "\
                    "level of {:.2f}% (min {:.2f}%)."\
                    .format(
                        moist,
                        plant.moist_level
                    ))
                break

    def _water_plant(self, plant) -> float:
        with Gardener.__watering_semaphore:
            old_state = plant.state
            plant.state = State.watering
            actual_ml = self.water_supply.watering(
                plant.pour_millilitres,
                plant.valve_pin
                )
            plant.state = old_state
        return actual_ml

    def _wait_for_tank(self) -> bool:
        '''
        Return False to indicate that watering must in canceled.
        Return True to indicate that tank is available.
        '''
        waiting = None
        while not self.water_supply.available_event.wait(0.1):
            if self.stop_event.is_set():
                result = False
                break
            if waiting is None:
                log.info(" watering cycle is waiting for tank to become available...")
                waiting = True
        else:
            result = True
        if waiting and result:
            log.debug(" ended waiting: tank became available.")
        elif waiting:
            log.debug(" tank waiting interrupted!")
        return result

    def close(self):
        my_name = self.__class__.__name__
        log.debug("Ending %s, quitting worker threads. Please wait..." % my_name)
        self.__worker_queue.join()
        if hasattr(self, 'water_supply'):
            self.water_supply.close()
        if hasattr(self, 'plants'):
            for p in self.plants:
                p.close()
        self.__db_worker_stop.set()
        with suppress(AttributeError):
            self.__db_thread.join()
        self.closed = True
        log.debug("Completed %s!" % my_name)


general_exc_msg = 'Exception occured: '
