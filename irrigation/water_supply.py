import logging
from contextlib import suppress
import queue
from threading import Thread, BoundedSemaphore
from gpiozero import OutputDevice
from .pumping import Pump
from .water_tank import WaterTank


class WaterSupply():
    def __init__(self, stop_event, pump_args, valve_pins, tank_args):
        self.closed = False
        self.stop_event = stop_event
        self.__pump_work = queue.Queue(maxsize=1)
        self.__pump_work_result = queue.Queue(maxsize=1)
        self.__semaphore = BoundedSemaphore(value=1)
        self.__valves = {}
        try:
            self.__pump = Pump(**pump_args)
            for pin in valve_pins:
                self.__valves[pin] = OutputDevice(pin)
            self.__pump_worker_thread = Thread(
                name = 'WaterSupply_PumpWorker',
                target = self.__pump_worker
                )
            self.__tank_thread = WaterTank(
                self.stop_event,
                **tank_args
                )
        except:
            self.close()
            raise
        self.available_event = self.__tank_thread.available_event
        self.__pump_worker_thread.start()
        self.__tank_thread.start()

    def __del__(self):
        if not self.closed:
            self.close()

    def __must_stop_pump(self) -> bool:
        return self.stop_event.is_set() or not self.available_event.is_set()

    def __pump_worker(self):
        try:
            while not self.stop_event.is_set():
                with suppress(queue.Empty):
                    args = self.__pump_work.get(timeout=0.1)
                    stats = self.__pump.pump_millilitres(*args)
                    self.__pump_work_result.put(stats)
        except:
            self.stop_event.set()
            logging.exception(general_exc_msg)
        finally:
            self.__pump.close()

    def watering(self, millilitres, valve_pin, pump_speed=1) -> float:
        with self.__semaphore:
            if self.__must_stop_pump():
                logging.debug("cannot start pump at this time!")
                return -1
            logging.debug("   started pumping.")
            self.__pump_work.put((
                millilitres,
                self.__valves[valve_pin],
                pump_speed
                ))
            while True:
                if self.__must_stop_pump():
                    self.__pump.reached_event.set()
                with suppress(queue.Empty):
                    stats = self.__pump_work_result.get(timeout=0.1)
                    break
            logging.info("   done, pumped {}ml in {:.3f} seconds.".format(*stats))
            return stats[0]

    def close(self):
        my_name = self.__class__.__name__
        logging.debug("Ending %s, quitting worker threads. Please wait..." % my_name)
        for d in self.__valves.values():
            d.close()
        with suppress(AttributeError):
            self.__pump.close()
            if self.__pump_worker_thread.is_alive():
                self.__pump_worker_thread.join()
            if self.__tank_thread.is_alive():
                self.__tank_thread.join()
        self.closed = True
        logging.debug("Completed %s!" % my_name)


general_exc_msg = 'Exception occured: '
