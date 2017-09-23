from threading import Thread, BoundedSemaphore
import queue
from hardware import Pump, WaterTank
from common import common_logger as log

from time import sleep

class WaterSupply():
    def __init__(self, stop_event, pump_args, tank_args):
        self.stop_event = stop_event
        self.__pump = Pump(**pump_args)
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

    def __must_stop_pump(self):
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

    def watering(self, millilitres, valve, pump_power):
        with self.__semaphore:
            if self.__must_stop_pump():
                log("cannot start pump at this time!")
                return
            log("   started pumping water.")
            self.__pump_work.put((millilitres, valve, pump_power))
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
            log("  ... %.3fml in %.3f seconds" % stats)
            log("   done pumping water.")

    def close(self):
        log("Ending WaterSupply, quitting worker thread. Please wait...\n")
        self.closed = False
        self.__pump_worker_thread.join()
        self.__tank_thread.join()
        self.closed = True
        log("Completed Gardener!\n")

    def __del__(self):
        if hasattr(self, 'closed') and not self.closed:
            self.close()
