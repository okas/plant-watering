from datetime import datetime, timedelta
from queue import Queue
from threading import Thread, Event
from gpiozero import DigitalInputDevice, OutputDevice
from .water_tank import WaterTank
from .plant import Plant, State
from hardware import Pump
from common import common_logger as log


class Gardener:
    def __init__(
        self,
        pump_args,
        tank_args,
        plants_args,
        watch_cycle=30,
        watering_cycle=2
        ):
        self.stop_event = Event()
        self.watering_event = Event()
        self.tank_avail_evt = Event()
        self.__water_tank_thread = WaterTank(
            self.stop_event,
            self.watering_event,
            self.tank_avail_evt,
            **tank_args
            )
        #self.pump = Pump()
        Plant.setup_shared_pump(pump_args)
        self.plants = self.__to_plants(plants_args)
        self.__plants_queue = self.__to_queue(self.plants)
        self.watch_cycle = watch_cycle
        self.watering_cycle = watering_cycle

    def __to_plants(self, plants_args):
        '''set up Plant object graph'''
        factory = lambda args: Plant(
            self.stop_event,
            self.watering_event,
            self.tank_avail_evt,
            **args
            )
        return tuple(factory(args) for args in plants_args)

    def __to_queue(self, plants):
        q = Queue()
        for p in plants:
            q.put(p)
        return q

    def start_work(self):
        self.__water_tank_thread.start()
        count = len(self.plants)
        log("Gardener is starting to watch for %d plants." % count)
        factory = lambda: _PlantWatcher(
            self.__plants_queue,
            self.stop_event,
            self.tank_avail_evt,
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
        self.__water_tank_thread.join()
        for p in self.plants: p.close()
        self.closed = True
        log("Completed Gardener!\n")

    def __del__(self):
        if hasattr(self, 'closed') and not self.closed: self.stop_and_close()


class _PlantWatcher(Thread):
    def __init__(self,  work_queue,  stop_event, tank_avail_evt, watch,  water):
        self.__work_queue = work_queue
        self.stop_event = stop_event
        self.tank_avail_evt = tank_avail_evt
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
            plant.watering()
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
        while not self.tank_avail_evt.wait(0.1):
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
