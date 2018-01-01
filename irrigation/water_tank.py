import logging
from enum import Enum, unique
from threading import Thread, Event
from gpiozero import RGBLED, DigitalInputDevice
from . common import stoppable_sleep
from . signals import irrigation_signals


log = logging.getLogger(__name__)
state_changed = irrigation_signals.signal('water_level_changed')


@unique
class State(Enum):
    not_measured = (0, 0, 0)
    empty        = (255, 5, 0)
    low          = (255, 30, 0)
    normal       = (0, 150, 0)
    full         = (0, 0, 150)
    sensor_error = (255, 0, 0)

    @property
    def rgb_floats(self):
        return tuple(1 * byte / 255 for byte in self.value)


## Consider refactor water tank that it internally spins up thread,
# instead of directly inheriting Thread class.
class WaterTank(Thread):
    def __init__(
            self,
            stop_event,
            probe_low_pin,
            probe_norm_pin,
            probe_full_pin,
            led_low_pin,
            led_norm_pin,
            led_full_pin,
            water_pour_time = 8
        ):
        self.closed = False
        self.__devices = {}
        try:
            self.__devices['low'] = DigitalInputDevice(probe_low_pin)
            self.__devices['norm'] = DigitalInputDevice(probe_norm_pin)
            self.__devices['full'] = DigitalInputDevice(probe_full_pin)
            self.__devices['led'] = RGBLED(led_low_pin, led_norm_pin, led_full_pin)
        except:
            self.close()
            raise
        self.stop_event = stop_event
        self.available_event = Event()
        self.__empty_to_low_event = Event()
        self.__state = State.not_measured
        self.__pouring_time = water_pour_time
        super().__init__(name=self.__class__.__name__)

    def __del__(self):
        if not self.closed:
            self.close()

    def __begin_running(self):
        log.debug("Started Water tank watcher thread.")
        self.measure()
        for p in self.probes:
            p.when_activated = p.when_deactivated = self.measure

    def __end_running(self):
        self.available_event.clear()
        self.close()
        log.debug("Completed Water tank watcher thread.")

    def _calculate_state(self, levels):
        if   levels == (False, False, False):
            return State.empty
        elif levels == (True, False, False):
            return State.low
        elif levels == (True, True, False):
            return State.normal
        elif levels == (True, True, True):
            return State.full
        else:
            return State.sensor_error

    def __needs_change(self, new_state, old_state):
        if new_state != State.empty and new_state == old_state:
            return False
        elif new_state == State.low and old_state == State.empty:
           self.__empty_to_low_event.set()
           return False
        elif new_state == State.empty and old_state == State.empty:
            self.__empty_to_low_event.clear()
            return False
        return True

    def __change_led(self, new_state, old_state):
        led = self.__devices['led']
        if new_state == State.empty:
            led.pulse(
                0.5,
                1.5,
                on_color = new_state.rgb_floats,
                off_color = (0.10,0,0),
                background = True
                )
        else:
            led.color = new_state.rgb_floats

    def __change_tank_availability(self, new_state):
        if new_state in (State.low, State.normal, State.full):
            self.available_event.set()
        else:
            self.available_event.clear()

    def run(self):
        try:
            self.__begin_running()
            stop_e = self.stop_event
            empt_e = self.__empty_to_low_event
            pouring_predicate = lambda: stop_e.is_set() or not empt_e.is_set()
            while not stop_e.wait(0.1):
                if not empt_e.is_set():
                    continue
                if not stoppable_sleep(self.__pouring_time, pouring_predicate):
                    self.state = State.low
                    empt_e.clear()
        except:
            stop_e.set()
            log.exception(general_exc_msg)
        finally:
            self.__end_running()

    def measure(self):
        if self.stop_event.is_set():
            log.debug("<object: WaterTank>.measure() execution canceled, "\
                "because stop event is set.")
            return
        levels = tuple(p.value for p in self.probes)
        new_state = self._calculate_state(levels)
        if self.__needs_change(new_state, self.state):
            self.state = new_state
        if new_state == State.sensor_error:
            self.stop_event.set()
            raise Exception(
                "Wrong sensor value reading: "\
                "low: %-5s | norm: %-5s | full: %-5s!\n"\
                "Investigate level probes physical placement "\
                "at tank or check connection pins!"\
                % levels
                )

    def close(self):
        for d in self.__devices.values():
            d.close()
        self.closed = True

    @property
    def probes(self):
        return (self.__devices[name] for name in ('low', 'norm', 'full'))

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, new_val):
        if self.stop_event.is_set():
            log.debug("<object: WaterTank>.state.setter attempt canceled, "\
                "because stop event is set.")
            return
        old_val = self.__state
        self.__state = new_val
        self.__change_tank_availability(new_val)
        self.__change_led(new_val, old_val)
        log.info('WaterTank state changed to [%s]' % new_val)
        state_changed.send(new_val)


general_exc_msg = 'Exception occured: '

if __name__ == "__main__":
    from time import sleep
    import sys
    import os
    sys.path.insert(1, os.path.realpath(__file__+'/../..'))


    probes = [16, 21, 20]
    rgb_led = [17, 27, 22]
    stop_event = Event()
    try:
        tank = WaterTank(
            stop_event,
            Event(),
            *probes,
            *rgb_led
            )
        tank.start()
        while tank.is_alive():
            sleep(0.2)
    finally:
        stop_event.set()
        tank.close()#redundant, here for testing!
