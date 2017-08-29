from time import sleep
from enum import Enum, unique
from threading import Thread, Event
from gpiozero import RGBLED
from common import common_logger as log, stoppable_sleep


# Todo: add logger implementation

@unique
class State(Enum):
    not_measured = 0
    empty = 1
    low = 2
    normal = 3
    full = 4
    sensor_error = 5


class Helpers():
    def rgb_conv(*args):
        return tuple(1 * byte / 255 for byte in args)


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
        self.__devices = dict(
            low = DigitalInputDevice(probe_low_pin),
            norm = DigitalInputDevice(probe_norm_pin),
            full = DigitalInputDevice(probe_full_pin),
            led = RGBLED(led_low_pin, led_norm_pin, led_full_pin)
        )
        for p in self.__probes:
            p.when_activated = p.when_deactivated = self.measure
        self.stop_event = stop_event
        self.watering_event = watering_event
        self.tank_avail_evt = tank_avail_evt
        self.__state = State.not_measured
        self.last_sensor_read = None
        self.measure()
        super().__init__()


    __state_rgb = {
        State.full         : (0, 0, 150),
        State.normal       : (0, 150, 0),
        State.low          : (255, 30, 0),
        State.empty        : (255, 0, 0),
        State.not_measured : (0, 0, 0),
        State.sensor_error : (255, 0, 0)
        }


    def run(self):
        log("Started Water tank watcher thread.")
        try:
            self.stop_event.wait()
        finally:
            self.tank_avail_evt.clear()
            self.stop_event.set()
            self.close()
            log("Completed Water tank watcher thread.")

    def __probes(self):
        return [d for k, d in self.__devices if k in ['low', 'norm', 'full']]

    def _change_led(self, new, old):
        state_color = Helpers.rgb_conv(__state_rgb[new])
        led = self.__devices['led']
        if new == State.sensor_error:
            if new == old:
                return
            led.blink(0.25, 0.25, on_color=state_color, off_color=(0,0,0))
            sleep(5)# FOR TESTING ONLY!!
            # TODO: Raise?
        else:
            led.color = state_color

    def __get_levels(self):
        result = tuple(
            self.__devices[p].value for p in self.__probes
        )
        self.last_sensor_read = datetime.now()
        return result

    def measure(self):
        if self.stop_event.is_set():
            return
        is_low, is_norm, is_full = self.__get_levels()
        if is_low and is_norm and is_full:
            self.state = State.full
            return False
        elif is_low and is_norm and not is_full:
            self.state = State.normal
            return False
        elif is_low and not is_norm and not is_full:
            self.state = State.low
            return True
        elif not is_low and not is_norm and not is_full:
            self.state = State.empty
            return True
        else:
            self.state = State.sensor_error
            raise Exception(
                "Wrong sensor value measured: low: %-5s | norm: %-5s | full: %-5s!\n"\
                "Investigate level probes physical placement "\
                "at tank or check connection pins!"\
                % is_low, is_norm, is_full
                )

    def join(self, timeout=None):
        self.stop_event.set()
        self.close()
        super().join(timeout)

    @property
    def state(self): return self.__state

    @state.setter
    def state(self, val):
        if not isinstance(val, State):
            log("Wrong Watertanks state provided: %s" % val)
            self.close()
            raise Exception("Should not end up here! Something is wrong with WaterTank instance state handling.")
        old_state = self.__state
        self.__state = val
        self._change_led(val, old_state)

    @property
    def closed(self):
        return all(d.closed for _, d in self.__devices)

    def close(self):
        if hasattr(self, 'closed') and not self.closed:
            for _, d in self.__devices:
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
        while True: sleep(0.333)
    finally:
        tank.close()
