import logging
from enum import Enum, unique
from time import time
from timeit import default_timer as timer
from threading import Lock
from gpiozero import PWMLED
from . soil_sensor import CapacitiveSensor
from . import signals


log = logging.getLogger(__name__)


@unique
class State(Enum):
    resting = 0
    watering = 1
    measuring = (0, 0, 0.05, 0.05)
    needs_water = (0, 0, 1, 1.5)


class Plant:
    def __init__(
            self,
            name,
            valve_pin,
            led_pin,
            moist_percent,
            sensor_args,
            pour_millilitres=50
            ):
        self.name = name
        self.sensor = CapacitiveSensor(**sensor_args)
        self.moist_level = moist_percent
        self.valve_pin = valve_pin
        self.pour_millilitres = pour_millilitres
        self.led = PWMLED(led_pin, frequency=100)
        self.next_action = time()
        self.__state_full = (State.resting, 0, 0)
        self.__measuring_lock = Lock()
        self.__state_lock = Lock()

    def __del__(self):
        if hasattr(self, 'closed') and not self.closed:
            self.close()

    def __measure(self, retain_state=False) -> tuple:
        self.__measuring_lock.acquire()
        preserved_state = self.__state_full
        self.state = State.measuring
        measure_moist = self.sensor.moisture_percent
        measure_time = time()
        if measure_moist > self.moist_level:
            new_state = State.resting
            result = False
        elif measure_moist <= self.moist_level:
            new_state = State.needs_water
            result = True
        if retain_state:
            self.state_full = preserved_state
        else:
            self.state_full = (new_state, measure_moist, measure_time)
        self.__measuring_lock.release()
        return (result, new_state, measure_moist, measure_time)

    def measure(self) -> bool:
        """
        Changes plant state.

        :returns:
            True if plant needs watering. Decision is based on
            sensor value, not recordered value.
        """
        return self.__measure(False)[0]

    def close(self):
        self.closed = False
        self.led.close()
        self.sensor.close()
        self.closed = True
        log.debug('Closed %s.' % self.name)

    @property
    def state(self) -> State:
        return self.__state_full[0]

    @state.setter
    def state(self, val):
        self.state_full = (val, *self.__state_full[1:])

    @property
    def moist(self) -> float:
        return self.__state_full[1]

    @property
    def moist_time(self) -> float:
        return self.__state_full[2]

    @property
    def state_full(self) -> tuple:
        """
        :returns:
            tuple(State, moist_percent, time_measured)
        """
        return self.__state_full

    @state_full.setter
    def state_full(self, val_tuple):
        with self.__state_lock:
            self.__state_full = val_tuple
            if isinstance(self.state.value, tuple):
                self.led.blink(*self.state.value)
            else:
                self.led.value = self.state.value
            signals.plant_status_changed.send(self)

    @property
    def state_full_measured(self) -> tuple:
        """
        Preservers plant state, only returns new full state.

        :returns:
            tuple(State, moist_percent, time_measured)
        """
        return self.__measure(retain_state=True)[1:]
