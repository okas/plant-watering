from time import sleep
from enum import Enum, unique
from datetime import datetime
from threading import Thread, Event
from gpiozero import RGBLED, DigitalInputDevice
if __name__ == "__main__":
    from sys import path as s_path
    from os import path as o_path
    s_path.insert(0, o_path.abspath(__file__+'/../..'))
from common import common_logger as log, stoppable_sleep


@unique
class State(Enum):
    not_measured = 0
    empty = 1
    low = 2
    normal = 3
    full = 4
    sensor_error = 5


class Helpers():
    __state_rgb = {
        State.full         : (0, 0, 150),
        State.normal       : (0, 150, 0),
        State.low          : (255, 30, 0),
        State.empty        : (255, 0, 0),
        State.not_measured : (0, 0, 0),
        State.sensor_error : (255, 0, 0)
        }

    def rgb_conv(*args):
        return tuple(1 * byte / 255 for byte in args)

    def get_state_rgb(state):
        return Helpers.rgb_conv(*Helpers.__state_rgb[state])


class WaterTank(Thread):
    def __init__(
            self,
            stop_event,
            watering_event,
            tank_avail_evt,
            probe_low_pin,
            probe_norm_pin,
            probe_full_pin,
            led_low_pin,
            led_norm_pin,
            led_full_pin
        ):
        self.__devices = {}
        try:
            self.__devices = dict(
                low = DigitalInputDevice(probe_low_pin),
                norm = DigitalInputDevice(probe_norm_pin),
                full = DigitalInputDevice(probe_full_pin),
                led = RGBLED(led_low_pin, led_norm_pin, led_full_pin)
                )
            for p in self.__probes:
                p.when_activated = p.when_deactivated = self.measure
        except:
            self.close()
            raise
        self.stop_event = stop_event
        self.watering_event = watering_event
        self.tank_avail_evt = tank_avail_evt
        self.__state = State.not_measured
        self.last_sensor_read = None
        super().__init__(name=self.__class__.__name__)

    def run(self):
        log("Started Water tank watcher thread.")
        self.measure()
        self.stop_event.wait()
        self.tank_avail_evt.clear()
        self.close()
        log("Completed Water tank watcher thread.")

    @property
    def __probes(self):
        return tuple(self.__devices[name] for name in ('low', 'norm', 'full'))

    def _change_led(self, new, old):
        state_color = Helpers.get_state_rgb(new)
        led = self.__devices['led']
        if new == State.sensor_error:
            if new == old:
                return
            led.pulse(
                0.25,
                0.25,
                on_color=state_color,
                off_color=(0,0,0),
                #n=10,
                background=True
                )
        else:
            led.color = state_color

    def __get_levels(self):
        result = tuple(p.value for p in self.__probes)
        self.last_sensor_read = datetime.now()
        return result

    def measure(self):
        if self.stop_event.is_set():
            return
        is_low, is_norm, is_full = self.__get_levels()
        if is_low and is_norm and is_full:
            self.state = State.full
        elif is_low and is_norm and not is_full:
            self.state = State.normal
        elif is_low and not is_norm and not is_full:
            self.state = State.low
        elif not is_low and not is_norm and not is_full:
            self.state = State.empty
        else:
            self.state = State.sensor_error
            self.stop_event.set()
            raise Exception(
                "Wrong sensor value measured: low: %-5s | norm: %-5s | full: %-5s!\n"\
                "Investigate level probes physical placement "\
                "at tank or check connection pins!"\
                % (is_low, is_norm, is_full)
                )
        log("Measured water levels: low: %-5s | norm: %-5s | full: %-5s"\
            % (is_low, is_norm, is_full)            )
        return True if self.state in [State.low, State.empty] else False

    @property
    def state(self): return self.__state

    @state.setter
    def state(self, val):
        if not isinstance(val, State):
            log("Wrong Watertanks state provided: %s" % val)
            self.close()
            raise Exception(
                "Should not end up here! Something is wrong "\
                "with WaterTank instance state handling."
                )
        old_state = self.__state
        self.__state = val
        self._change_led(val, old_state)

    def close(self):
        for d in self.__devices.values():
            d.close()

    def __del__(self):
        self.close()


if __name__ == "__main__":
    probes = [16, 21, 20]
    rgb_led = [17, 27, 22]
    stop_event = Event()
    try:
        tank = WaterTank(
            stop_event,
            Event(),
            Event(),
            *probes,
            *rgb_led
            )
        tank.start()
        while tank.is_alive(): sleep(0.2)
    finally:
        stop_event.set()
        tank.close()#redundant, here for testing!
