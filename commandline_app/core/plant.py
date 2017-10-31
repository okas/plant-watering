from enum import Enum, unique
from timeit import default_timer as timer
from threading import Lock
from gpiozero import PWMLED
from hardware import CapacitiveSensor
from common import common_logger as log, stoppable_sleep


@unique
class State(Enum):
    resting = 0
    watering = 1
    measuring = (0, 0, 0.05, 0.05)
    needs_water = (0, 0, 1, 1.5)


class Plant:
    def __init__(
            self,
            stop_event,
            id,
            valve_pin,
            led_pin,
            moist_percent,
            sensor_args,
            pour_millilitres=50
            ):
        self.stop_event = stop_event
        self.id = id
        self.sensor = CapacitiveSensor(**sensor_args._asdict())
        self.moist_level = moist_percent
        self.valve_pin = valve_pin
        self.pour_millilitres = pour_millilitres
        self.led = PWMLED(led_pin, frequency=100)
        self.sensor = SoilSensor(sensor_vcc_pin, **spi_args)
        self.__state = State.resting
        self.__p_state = None
        self.__measuring_lock = Lock()
        self.__state_lock = Lock()

    def __del__(self):
        if hasattr(self, 'closed') and not self.closed:
            self.close()

    def measure(self, retain_state=False) -> tuple:
        with self.__measuring_lock:
            self.__p_state = self.state
            self.state = State.measuring
            moist = self.sensor.moisture_percent
            if moist > self.moist_level:
                new_state = State.resting
                result = False
            elif moist <= self.moist_level:
                new_state = State.needs_water
                result = True
            else:
                log(' %s, state: %s, moisture: %s, sensor: %s'
                    % (self.id, self.state, self.moist_level, moist))
                raise Exception('Should not end up here! Something is '\
                                'wrong with Plant instance state handling.')
            self.state = self.__p_state if retain_state else new_state
            self.__p_state = None
        return (result, moist)

    def close(self):
        self.closed = False
        self.led.close()
        self.sensor.close()
        self.closed = True
        log('Closed %s.' % self.id)

    @property
    def state(self) -> State:
        return self.__state

    @state.setter
    def state(self, val):
        with self.__state_lock:
            self.__state = val
            if isinstance(val.value, tuple):
                self.led.blink(*val.value)
            else:
                self.led.value = val.value
