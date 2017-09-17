from enum import Enum, unique
from time import sleep
from timeit import default_timer as timer
from threading import BoundedSemaphore
from gpiozero import PWMLED, OutputDevice
from hardware import Pump, SoilSensor
from common import common_logger as log, stoppable_sleep


# Kill watering itself, someow. with button also?
# Name properly button thread

@unique
class State(Enum):
    resting = 0
    watering = 1
    remeasure = 2
    needs_water = 3


class Plant:
    blink_args = (0, 0, 1, 1.5)
    shared_pump = None
    __watering_semaphore = BoundedSemaphore(value=1) # we allow one pump user at the time

    def __init__(self,
                 stop_event,
                 watering_event,
                 tank_avail_evt,
                 id,
                 sensor_vcc_pin,
                 valve_pin,
                 led_pin,
                 button_pin,
                 moist_percent,
                 watering_time=5,
                 pump_power=0.5,
                 **spi_args):
        self.id = id
        self.led = PWMLED(led_pin, frequency=145)
        self.valve = OutputDevice(valve_pin)
        self.sensor = SoilSensor(sensor_vcc_pin, **spi_args)
        self.button = Button(button_pin, self)
        self.state = State.resting
        self.moist_level = moist_percent
        self.stop_event = stop_event
        self.watering_event = watering_event
        self.tank_avail_evt = tank_avail_evt
        self.watering_time = watering_time
        self.pump_power = pump_power
        self.button.when_pressed = _button_pressed

    @property
    def state(self): return self.__state

    @state.setter
    def state(self, val):
        if val == State.resting:
            self.led.off()
        elif val == State.watering:
            self.led.on()
        elif val == State.remeasure:
            self.led.blink(*Plant.blink_args)
        self.__state = val

    @classmethod
    def setup_shared_pump(cls, pin):
        cls.shared_pump = Pump(pin)

    def measure(self, retain_state=False):
        moist = self.sensor.moisture_percent
        if moist > self.moist_level:
            if not retain_state:
                self.state = State.resting
            return (False, moist)
        elif moist <= self.moist_level:
            if not retain_state:
                self.state = State.needs_water
            return (True, moist)
        else:
            log("id: %s, state: %s, moisture: %s, sensor: %s"\
                  % (self.id, self.state, self.moist_level, self.sensor.moisture_percent))
            raise Exception("Should not end up here!"\
                            "Something is wrong with Plant instance state handling.")
    def __cannot_pump(self):
        return self.stop_event.is_set() or not self.tank_avail_evt.is_set()

    def watering(self, override=False):
        # led-to-led context manager
        with Plant.__watering_semaphore:
            self.watering_event.set()
            # replace with self.watering_event.wait() ?
            sleep(0.2)# it must allow Event.set() to popagate to WaterTank
            if self.__cannot_pump():
                log("cannot start pump at this time!")
            else:
                old_state = self.state
                self.state = State.watering
                log("   started pumping water.")
                self.valve.on()
                t1 = timer()
                Plant.shared_pump.value = self.pump_power
                stoppable_sleep(self.watering_time, self.__cannot_pump)
                t2 = timer()
                log("  ... %.3f seconds" % (t2 - t1))
                Plant.shared_pump.off()
                self.valve.off()
                self.state = State.remeasure if not override else old_state
                log("   done pumping water.")
            self.watering_event.clear()

    def close(self):
        self.closed = False
        self.led.close()
        self.valve.close()
        self.sensor.close()
        self.button.close()
        self.closed = True
        log("Closed %s" % self.id)

    def __del__(self):
        if hasattr(self, 'closed') and not self.closed: self.close()


def _button_pressed(btn):
    log("- button is held...")
    while btn.is_pressed:
        btn.parent.watering(True)
        sleep(0.01)
    log("- button is released.")
