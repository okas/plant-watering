import queue
from threading import Thread, BoundedSemaphore
from gpiozero import OutputDevice
from hardware import Pump, WaterTank
from common import common_logger as log


class WaterSupply():
    def __init__(self, stop_event, pump_args, valve_pins, tank_args):
        self.closed = False
        self.__valves = {}
        try:
            self.__pump = Pump(**pump_args)
            for pin in valve_pins:
                self.__valves[pin] = OutputDevice(pin)
        except:
            self.close()
            raise
        self.stop_event = stop_event
        self.__pump_work = queue.Queue(maxsize=1)
        self.__pump_work_result = queue.Queue(maxsize=1)
        self.__semaphore = BoundedSemaphore(value=1)
        self.__pump_worker_thread = Thread(
            name = 'WaterSupply_PumpWorker',
            target = self.__pump_worker
            )
        self.__tank_thread = WaterTank(
            self.stop_event,
            **tank_args
            )
        self.available_event = self.__tank_thread.available_event
        self.__pump_worker_thread.start()
        self.__tank_thread.start()

    def __del__(self):
        if hasattr(self, 'closed') and not self.closed:
            self.close()

    def __must_stop_pump(self) -> bool:
        return self.stop_event.is_set() or not self.available_event.is_set()

    def __pump_worker(self):
        while not self.stop_event.is_set():
            try:
                args = self.__pump_work.get(timeout=0.1)
            except queue.Empty:
                pass
            else:
                stats = self.__pump.pump_millilitres(*args)
                self.__pump_work_result.put(stats)
        self.__pump.close()

    def watering(self, millilitres, valve_pin, pump_speed=1) -> float:
        with self.__semaphore:
            if self.__must_stop_pump():
                log("cannot start pump at this time!")
                return -1
            log("   started pumping water.")
            self.__pump_work.put((
                millilitres,
                self.__valves[valve_pin],
                pump_speed
                ))
            stats = None
            while True:
                if self.__must_stop_pump():
                    self.__pump.reached_event.set()
                try:
                    stats = self.__pump_work_result.get(timeout=0.1)
                except queue.Empty:
                    pass
                else:
                    break
            log("  ... {}ml in {:.3f} seconds".format(*stats))
            log("   done pumping water.")
            return stats[0]

    def close(self):
        my_name = self.__class__.__name__
        log("Ending %s, quitting worker threads. Please wait..." % my_name)
        self.__pump.close()
        for d in self.__valves.values():
            d.close()
        self.__pump_worker_thread.join()
        self.__tank_thread.join()
        self.closed = True
        log("Completed %s!" % my_name)
