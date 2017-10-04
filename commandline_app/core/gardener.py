from datetime import datetime, timedelta
from queue import Queue
from threading import Thread, Event, BoundedSemaphore
from .plant import Plant, State
from .water_supply import WaterSupply
from common import common_logger as log


def add_seconds(s:float, format='%X') -> str:
    return (datetime.now() + timedelta(seconds=s)).strftime(format)


class Gardener:
    __watering_semaphore = BoundedSemaphore(value=1)

    def __init__(self, config):
        self.closed = False
        self.watch_cycle = config.gardener_args.watch_cycle
        self.watering_cycle = config.gardener_args.watering_cycle
        self.stop_event = Event()
        self.water_supply = WaterSupply(
            self.stop_event,
            config.pump_args._asdict(),
            (p.valve_pin for p in config.plants_args_list),
            config.tank_args._asdict()
            )
        self.plants = self.__init_plants(config.plants_args_list)
        self.__worker_queue = Queue()
        self.__start_work()

    def __del__(self):
        if not self.closed:
            self.stop_event.set()
            self.close()

    def __init_plants(self, a_list) -> tuple:
        return tuple(Plant(self.stop_event, **a._asdict()) for a in a_list)

    def __start_work(self):
        for plant in self.plants:
            self.__worker_queue.put(plant)
            Thread(
                name = "[{}_worker]".format(plant.id),
                target = self.plant_watcher_worker
                ).start()
        log("Gardener is starting to watch for %d plants."\
            % len(self.plants))

    def plant_watcher_worker(self):
        plant = self.__worker_queue.get()
        while not self.stop_event.is_set():
            moist = plant.measure()[1]
            if plant.state == State.needs_water:
                self.handle_watering_cycle(plant)
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

    def handle_watering_cycle(self, plant):
        '''Perform watering, measuring and re-watering if neccessary.'''
        log(" Start watering cycles.")
        while True:
            if not self.wait_for_tank():
                log(" stopping watering cycle, because something asked.")
                break
            log("  start watering.")
            with Gardener.__watering_semaphore:
                self.water_plant(plant)
            log("  watering cycle, next measure at %s."
                % add_seconds(self.watering_cycle))
            if self.stop_event.wait(self.watering_cycle):
                log(" stopping watering cycle, because something asked.")
                break
            measure, moist = plant.measure()
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

    def water_plant(self, plant):
        old_state = plant.state
        plant.state = State.watering
        self.water_supply.watering(plant.pour_millilitres, plant.valve_pin)
        plant.state = old_state

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
        self.water_supply.close()
        for p in self.plants:
            p.close()
        self.closed = True
        log("Completed %s!" % my_name)
