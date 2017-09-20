from datetime import datetime, timedelta
from queue import Queue
from threading import Thread, Event
from gpiozero import DigitalInputDevice, OutputDevice
from .plant import Plant, State
from .water_supply import WaterSupply
from common import common_logger as log


class Gardener:
    def __init__(config):
        ## evaluae all these event usages in this class!
        self.stop_event = Event()
        self.water_supply = WaterSupply(
            self.stop_event,
            config['pump_args'],
            config['tank_args']
            )
        self.plants = self.__to_plants(config['plants_args'])
        self.__plants_queue = self.__to_queue(self.plants)
        self.watch_cycle = config['gardener_args'].watch_cycle
        self.watering_cycle = config['gardener_args'].watering_cycle
        self.__start_work()

    def __to_plants(self, plants_args):
        '''set up Plant object graph'''
        factory = lambda args: Plant(
            self.stop_event,
            **args
            )
        return tuple(factory(args) for args in plants_args)

    def __to_queue(self, plants):
        q = Queue()
        for p in plants:
            q.put(p)
        return q

    def __start_work(self):
        count = len(self.plants)
        log("Gardener is starting to watch for %d plants." % count)
        factory = lambda: _PlantWatcher(
            self.__plants_queue,
            self.stop_event,
            self.water_supply,
            self.watch_cycle,
            self.watering_cycle
            )
        for _ in range(count):
            factory().start()

    def stop_and_close(self):
        log("Ending Gardener, quitting worker threads. Please wait...\n")
        self.closed = False
        self.stop_event.set()
        self.__plants_queue.join()
        self.water_supply.stop_and_close()
        for p in self.plants:
            p.close()
        self.closed = True
        log("Completed Gardener!\n")

    def __del__(self):
        if hasattr(self, 'closed') and not self.closed: self.stop_and_close()


class _PlantWatcher(Thread):
    def __init__(self,  work_queue,  stop_event, water_supply, watch,  water):
        self.__work_queue = work_queue
        self.stop_event = stop_event
        self.water_supply = water_supply
        self.watch = watch
        self.water = water
        self.plant = work_queue.get()
        super().__init__(name=self.plant.id+"_pw")

    def add_seconds(self, seconds, strftime="%X"):
        return (datetime.now() + timedelta(seconds=seconds)).strftime(strftime)

    def run(self):
        try:
            while not self.stop_event.is_set():
                moist = self.plant.measure()[1]
                if self.plant.state == State.needs_water:
                    self.water_plant(self.plant)
                    if self.stop_event.is_set(): break
                    log("in watch cycle, next measure at %s." % self.add_seconds(self.watch))
                else:
                    log("watch cycle completed, plant has enough moisture %.2f%% (min %.2f%%),"\
                        "next measure at %s." % (moist, self.plant.moist_level, self.add_seconds(self.watch)))
                if self.stop_event.wait(self.watch):
                    log("stopping watcher cycle, because something asked.")
                    break
        finally:
            self.stop_event.set()
            self.__work_queue.task_done()
        log("Completed PlantWatcher thread.")

    def water_plant(self, plant):
        '''Perform watering, measuring and re-watering if neccessary.'''
        log("Start watering cycles.")
        while True:
            if not self.wait_for_tank():
                log("stopping watering cycle, because something asked.")
                break
            log(" start watering.")
            self.water_supply.watering(plant)
            log(" watering cycle, next measure at %s." % self.add_seconds(self.water))
            if self.stop_event.wait(self.water):
                log("stopping watering cycle, because something asked.")
                break
            measure, moist = self.plant.measure()
            if not measure:
                log("watering cycle completed, plant reached moisture level of %.2f%% (min %.2f%%), "\
                    "next measure at %s." % (moist, self.plant.moist_level, self.add_seconds(self.watch)))
                break
        plant.led.off()
        log("Completed watering.")

    def wait_for_tank(self):
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
                log("watering cycle is waiting for tank to become available...")
                waiting = True
        else:
            result = True
        if waiting and result:
            log("ended waiting: tank became available.")
        elif waiting:
            log("tank waiting interrupted!")
        return result
