from enum import Enum, unique
from timeit import default_timer as timer
from gpiozero import PWMLED, OutputDevice
from hardware import SoilSensor
from common import common_logger as log, stoppable_sleep


@unique
class State(Enum):
    resting = 0
    watering = 1
    measuring = (0, 0, 0.15, 0.35)
    needs_water = (0, 0, 1, 1.5)


class Plant:
    def __init__(
            self,
            stop_event,
            id,
            sensor_vcc_pin,
            valve_pin,
            led_pin,
            moist_percent,
            pour_millilitres=50,
            **spi_args
            ):
        self.id = id
        self.led = PWMLED(led_pin, frequency=100)
        self.valve = OutputDevice(valve_pin)
        self.sensor = SoilSensor(sensor_vcc_pin, **spi_args)
        self.state = State.resting
        self.moist_level = moist_percent
        self.stop_event = stop_event
        self.pour_millilitres = pour_millilitres
        self.__measuring_semaphore = BoundedSemaphore(value=1)

    def __del__(self):
        if hasattr(self, 'closed') and not self.closed:
            self.close()

    def measure(self, retain_state=False):
        with self.__measuring_semaphore:
            old_state = self.state
            self.state = State.measuring
            moist = self.sensor.moisture_percent
            if moist > self.moist_level:
                new_state = State.resting
                result = False
            elif moist <= self.moist_level:
                new_state = State.needs_water
                result = True
            else:
                log("id: %s, state: %s, moisture: %s, sensor: %s"\
                    % (self.id, self.state, self.moist_level, moist))
                raise Exception("Should not end up here! Something is "\
                                "wrong with Plant instance state handling.")
            self.state = old_state if retain_state else new_state
            return (result, moist)

    def close(self):
        self.closed = False
        self.led.close()
        self.valve.close()
        self.sensor.close()
        self.closed = True
        log("Closed %s." % self.id)

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, val):
        self.__state = val
        if isinstance(val.value, tuple):
            self.led.blink(*val.value)
        else:
            self.led.value = val.value
