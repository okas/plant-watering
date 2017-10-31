import os
import typing
import uuid
from datetime import datetime, timedelta
import queue
from threading import Thread, Event, BoundedSemaphore
from unqlite import UnQLite
from .plant import Plant, State
from .water_supply import WaterSupply
from common import common_logger as log


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
        self._db__id = None
        self.__init_db('{}/../../data/{}.db'.format(__file__, config.name))
        self.watch_cycle = config.gardener_args.watch_cycle
        self.watering_cycle = config.gardener_args.watering_cycle
        self.water_supply = WaterSupply(
            self.stop_event,
            config.pump_args._asdict(),
            (p.valve_pin for p in config.plants_args_list),
            config.tank_args._asdict()
            )
        self.plants = tuple(self.__init_plants(config.plants_args_list))
        self.__start_work_data()
        self.__start_work_watchers()

    def __del__(self):
        if not self.closed:
            self.stop_event.set()
            self.close()

    def __init_db(self, db_path):
        self.__db = UnQLite(os.path.abspath(db_path))
        self.__db.collection('gardener_instances').create()

    def __init_plants(self, a_list) -> typing.Iterator[Plant]:
        for a in a_list:
            p = Plant(self.stop_event, **a._asdict())
            p.uuid1 = uuid.uuid1()
            yield p

    def __start_work_data(self):
        gardener_record = {
            'uuid1': str(uuid.uuid1()),
            'watch_cycle': self.watch_cycle,
            'watering_cycle': self.watering_cycle,
            'plants':
                list({
                    'uuid1': str(p.uuid1),
                    'name': p.name,
                    'moist_level': p.moist_level
                    } for p in self.plants
                )
            }
        with self.__db.transaction():
            self._db__id = self.__db\
                .collection('gardener_instances')\
                .store(gardener_record)
        self.__db_thread = Thread(
            name = '_db_worker',
            target = self.__db_worker
            )
        self.__db_thread.start()

    def __db_worker(self):
        log('Started database worker.')
        while not self.__db_worker_stop.is_set():
            try:
                work = self.__db_queue.get(timeout=0.1)
            except queue.Empty:
                pass
            else:
                work()
        self.__db.close()
        log('Completed database worker.')

    def __start_work_watchers(self):
        for plant in self.plants:
            self.__worker_queue.put(plant)
            Thread(
                name = "[{}_worker]".format(plant.name),
                target = self.plant_watcher_worker
                ).start()
        log("Gardener is starting to watch for %d plants."\
            % len(self.plants))

    def _get_collections(self) -> tuple:
        measur = self.__db.collection('plant_moisture_measurements')
        water = self.__db.collection('plant_waterings')
        measur.create()
        water.create()
        return (measur, water)

    def _save_measure(self, coll_moist, p_uuid1, moist):
        @self.__db.commit_on_success
        def measure_commiter():
            coll_moist.store({
                'gardener__id': str(self._db__id),
                'plant_uuid1': str(p_uuid1),
                'ts_utc': datetime.utcnow().timestamp(),
                'percent': moist
                })
        self.__db_queue.put(measure_commiter)

    def _save_watering(self, coll_water, p_uuid1, water):
        @self.__db.commit_on_success
        def water_commiter():
            coll_water.store({
                'gardener__id': str(self._db__id),
                'plant_uuid1': str(p_uuid1),
                'ts_utc': datetime.utcnow().timestamp(),
                'mil_lit': water
                })
        self.__db_queue.put(water_commiter)

    def plant_watcher_worker(self):
        plant = self.__worker_queue.get()
        db_coll_moist, db_coll_water = self._get_collections()
        while not self.stop_event.is_set():
            moist = plant.measure()[1]
            self._save_measure(db_coll_moist, plant.name, moist)
            if plant.state == State.needs_water:
                self.handle_watering_cycle(plant, db_coll_moist, db_coll_water)
                if self.stop_event.is_set():
                    break
                log(" in watch cycle, next measure at %s."\
                    % add_seconds(self.watch_cycle))
            else:
                log(" watch cycle completed, plant has enough "\
                    "moisture {:.2f}% (min {:.2f}%), "\
                    "next measure at {}."\
                    .format(
                        moist,
                        plant.moist_level,
                        add_seconds(self.watch_cycle)
                    ))
            if self.stop_event.wait(self.watch_cycle):
                log(" stopping watcher cycle, because something asked.")
                break
        self.stop_event.set()
        self.__worker_queue.task_done()
        log(" completed plant watcher thread.")

    def handle_watering_cycle(self, plant, db_coll_moist, db_coll_water):
        '''Perform watering, measuring and re-watering if neccessary.'''
        log(" Start watering cycles.")
        while True:
            if not self.wait_for_tank():
                log(" stopping watering cycle, because something asked.")
                break
            log("  start watering.")
            actual_ml = self.water_plant(plant)
            self._save_watering(db_coll_water, plant.uuid1, actual_ml)
            log("  watering cycle, next measure at %s."
                % add_seconds(self.watering_cycle))
            if self.stop_event.wait(self.watering_cycle):
                log(" stopping watering cycle, because something asked.")
                break
            measure, moist = plant.measure()
            self._save_measure(db_coll_moist, plant.uuid1, moist)
            if not measure:
                log(" watering cycle completed, reached moisture "\
                    "level of {:.2f}% (min {:.2f}%), "\
                    "next measure at {}."\
                    .format(
                        moist,
                        plant.moist_level,
                        add_seconds(self.watch_cycle)
                    ))
                break
        log(" Completed watering.")

    def water_plant(self, plant) -> float:
        with Gardener.__watering_semaphore:
            old_state = plant.state
            plant.state = State.watering
            actual_ml = self.water_supply.watering(
                plant.pour_millilitres,
                plant.valve_pin
                )
            plant.state = old_state
        return actual_ml

    def wait_for_tank(self) -> bool:
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
                log(" watering cycle is waiting for tank to become available...")
                waiting = True
        else:
            result = True
        if waiting and result:
            log(" ended waiting: tank became available.")
        elif waiting:
            log(" tank waiting interrupted!")
        return result

    def close(self):
        my_name = self.__class__.__name__
        log("Ending %s, quitting worker threads. Please wait..." % my_name)
        self.__worker_queue.join()
        if hasattr(self, 'water_supply'):
            self.water_supply.close()
        if hasattr(self, 'plants'):
            for p in self.plants:
                p.close()
        self.__db_worker_stop.set()
        self.__db_thread.join()
        self.closed = True
        log("Completed %s!" % my_name)
