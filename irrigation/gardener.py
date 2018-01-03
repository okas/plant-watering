import logging
import os
from time import time, localtime, strftime
import uuid
from contextlib import suppress
from datetime import datetime
import queue
from threading import currentThread, Thread, Event, BoundedSemaphore
from unqlite import UnQLite
from . plant import Plant, State
from . water_supply import WaterSupply
from . signals import irrigation_signals


log = logging.getLogger(__name__)
general_exc_msg = 'Exception occured: '


class Gardener:
    __watering_semaphore = BoundedSemaphore(value=1)

    def __init__(self, config):
        self.closed = False
        self.stop_event = Event()
        self.__db_worker_stop = Event()
        self.__worker_queue = queue.Queue()
        self.__db_queue = queue.Queue()
        self.watch_cycle = config['gardener_args']['watch_cycle']
        self.watering_cycle = config['gardener_args']['watering_cycle']
        self.plants = tuple(Plant(**pa) for pa in config['plants_args_list'])
        self.__consumed_water = 0
        self._db__id = None
        self.__db_thread = None
        self.db = self.__init_db(config['database_dir'], config['name'])
        self.water_supply = WaterSupply(
            self.stop_event,
            config['pump_args'],
            (p['valve_pin'] for p in config['plants_args_list']),
            config['tank_args']
            )
        self.__start_work_data()
        Thread(name='PlantWatcher', target=self.__watcher_loop_thread).start()

    def __del__(self):
        if not self.closed:
            self.stop_event.set()
            self.close()

    def __init_db(self, database_dir, name):
        if not (os.path.isabs(database_dir) and
                os.path.isdir(database_dir)):
            raise OSError('Expected existing and absolute directory '\
                          'path, instead of "%s"' % database_dir)
        db = UnQLite(os.path.join(database_dir, name+'.bson'))
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

    def __watcher_loop_thread(self):
        '''
        Main watcher loop, keep as performant as possible!
        All plants are in here at 'resting' or 'needs_water' state.
        '''
        log.info('Starting to watch for %d plants.'\
            % len(self.plants))
        while not self.stop_event.wait(0.1):
            current_time = time()
            for plant in (p for p in self.plants if p.next_action != 0):
                if current_time > plant.next_action:
                    plant.next_action = 0
                    self.__worker_queue.put(plant)
                    Thread(target = self.plant_worker_thread).start()
        notify = [p.name for p in self.plants if p.state != State.resting]
        if len(notify) > 0:
            log.debug('  these plants were proccesed during '\
                'interruption request: %s' % ', '.join(notify))
        log.debug('Completed PlantWatcher.')

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

    def plant_worker_thread(self):
        plant = self.__worker_queue.get()
        currentThread().name = "{}[w]".format(plant.name)
        try:
            old_state = plant.state
            needs_watering = plant.measure()
            self._save_measure(plant.uuid1, plant.moist)
            if needs_watering:
                self._handle_watering_phase(plant, old_state)
            else:
                self._handle_resting_phase(plant, old_state)
        except:
            self.stop_event.set()
            log.exception(general_exc_msg)
        finally:
            self.__worker_queue.task_done()

    def _handle_watering_phase(self, plant, old_state):
        if old_state == State.resting:
            log.info(' Entered watering phase, moisture low: '
                '{p.moist:.2f}% (min {p.moist_level:.2f}%).'.format(p=plant))
        if not self._wait_for_tank():
            return
        log.debug('  start watering.')
        actual_ml = self._water_plant(plant)
        plant.next_action = time() + self.watering_cycle
        self._save_watering(plant.uuid1, actual_ml)
        log.info('  re-measure moisture at {t}, current moisture: '\
            '{p.moist:.2f}%.'.format(p=plant,
                t=strftime('%X', localtime(plant.next_action))))
        self.water_consumed = actual_ml

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

    def _handle_resting_phase(self, plant, old_state):
        plant.next_action = time() + self.watch_cycle
        if old_state == State.needs_water:
            msg1 = ' plant reached moisture level of {p.moist:.2f}% '\
                '(min {p.moist_level:.2f}%), re-measure at {t}.'
        else:
            msg1 = ' Enough moisture {p.moist:.2f}% (min {p.moist_level:.2f}%), '\
                're-measure at {t}.'
        log.info(msg1.format(p=plant,
            t=strftime('%X', localtime(plant.next_action))))

    def _wait_for_tank(self) -> bool:
        '''
        :returns:
            False to indicate that stop event is set -- close ASAP.
            True to indicate that tank is vailable (or bacame after waiting).
        '''
        waiting = None
        while not self.water_supply.available_event.wait(0.1):
            if self.stop_event.is_set():
                result = False
                break
            if waiting is None:
                log.info(' watering cycle is waiting for tank to become available...')
                waiting = True
        else:
            result = True
        if waiting and result:
            log.debug(' ended waiting: tank became available.')
        elif waiting:
            log.debug(' tank waiting interrupted!')
        return result

    def close(self):
        my_name = self.__class__.__name__
        log.debug('Ending %s, quitting worker threads. Please wait...'
            % my_name)
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
        log.debug('Completed %s!' % my_name)

    @property
    def water_consumed(self):
        return self.__consumed_water

    @water_consumed.setter
    def water_consumed(self, addVal):
        self.__consumed_water += addVal
        irrigation_signals\
            .signal('water_consumed_changed')\
            .send(round(self.__consumed_water, 0))
