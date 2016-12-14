from time import sleep
from enum import Enum, unique
from threading import Thread, Event
from gpiozero import RGBLED
from common import common_logger as log, stoppable_sleep
from hardware import LevelSensor, Valve

# Todo: add logger implementation

@unique
class State(Enum):
    not_measured = 0
    empty = 1
    low = 2
    normal = 3
    full = 4
    sensor_error = 5


class WaterTank(Thread):
    __count_inst = 1
    def __init__(self,
                 stop_event,
                 watering_event,
                 tank_avail_evt,
                 probe_vcc_pin,
                 probe_low_pin,
                 probe_norm_pin,
                 probe_full_pin,
                 led_low_pin,
                 led_norm_pin,
                 led_full_pin,
                 valve_pin=None,
                 standby_interval = 60,
                 empty_interval = 10,
                 active_interval = 0.25):
        if valve_pin is not None:
            self.__valve = Valve(valve_pin)
            self.__filler_thread = Thread(name="TankFiller", target=self.fill_worker)
        else:
            self.__valve = None
        self.__sensor = LevelSensor(probe_vcc_pin, probe_low_pin, probe_norm_pin, probe_full_pin)
        self.__led = RGBLED(led_low_pin, led_norm_pin, led_full_pin)
        self.stop_event = stop_event
        self.watering_event = watering_event
        self.tank_avail_evt = tank_avail_evt
        self.fill_event = Event()
        self.standby_interval = standby_interval
        self.empty_interval = empty_interval
        self.active_interval = active_interval
        self.__state = State.not_measured
        super().__init__(name="%s-%s" % (self.__class__.__name__, WaterTank.__count_inst))
        WaterTank.__count_inst += 1

    def run(self):
        # todo:
        # inactive workflow is to just long cycle iterations
        # active workflows, they use times > 1 per second measurements
        # 1. watering
        # 2. filling
        # ***************
        # any measuring puts tank temporarily to tank_avial_evt.wait(). Is it possible?
        # ***************
        # active flows do both:
        # - use high speed measurements
        # - LED flashes in a way where color shows actual level during slow pulsing
        # - LED restores normal color accorgind to water level
        # watering flow does:
        # - when water is in or reashes 'low' state then set the watering evet (stop pump)
        #********************
        # differentiate fatal error condition an teardown:
        # a. if tank is in active state then error in sensor reading must stopp watering
        # - and filling
        # - follows evaluation on sensor. If seems contextually OK, watering vs. filling,
        # - then try to resume operation.
        # - When sensor gives repeatitive errors then halt all program
        # b. backgroung states should only perform some light evaluation. Only repeatitive
        # - error in sensor must halt all programm
        if self.__valve is not None: self.__filler_thread.start()
        log("Started Water tank watcher and filler threads.")
        try:
            while not self.stop_event.is_set():
                if self.measure():
                    self.__handle_filling()
                else:
                    self.__handle_availability()
                self.__handle_waiting()
        finally:
            self.tank_avail_evt.clear()
            self.stop_event.set()
            if self.__valve is not None: self.__filler_thread.join()
            self.close()
            log("Completed Water tank watcher and filler threads.")

    def __handle_filling(self):
        if self.state == State.empty or (self.__valve is not None and self.state == State.low):
            self.tank_avail_evt.clear()
        if self.__valve is not None:
            self.fill_event.set()
        elif self.state == State.low:
            self.tank_avail_evt.set()

    def __handle_availability(self):
        if self.state == State.full:
            self.fill_event.clear()
        if not self.fill_event.is_set():
            self.tank_avail_evt.set()

    def __handle_waiting(self):
        if self.fill_event.is_set() or self.watering_event.is_set():
            self.stop_event.wait(self.active_interval)
        elif self.state == State.empty:
            self.stop_event.wait(self.empty_interval)
        else:
            stoppable_sleep(self.standby_interval, self.__stop_waiting)
            
    def __stop_waiting(self):
        return self.stop_event.is_set() or self.watering_event.is_set()
        
    def fill_worker(self):
        filling = False
        while not self.stop_event.is_set():
            self.fill_event.wait(0.2)
            if self.fill_event.is_set() and not filling:
                filling = True
                #self._change_filling_led(state=self.state)
                log("Started filling")
                # -- Todo: actuator on()
            elif not self.fill_event.is_set() and filling:
                filling = False
                # -- Todo: actuator off()
                log("Completed filling")
      
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

    def _change_led(self, new, old):
        state_color = self._get_state_color(new)
        if new == State.sensor_error:
            if new == old: return
            self.__led.blink(0.25, 0.25, on_color=state_color, off_color=(0,0,0))
            sleep(5)# FOR TESTING ONLY!!
            # TODO: Raise?
        elif self.fill_event.is_set():
            if new == old and self.__led._blink_thread is not None: return
            self._change_filling_led(color=state_color)
        else:
            self.__led.color = state_color

    def _change_filling_led(self, state=None, color=None):
        #if self.__led._blink_thread is not None: return
        state_color = color if color is not None else self._get_state_color(state)
        self.__led.blink(0.35, 0.35, 0.15, 0.15, on_color=(0.9,0.9,0.9), off_color=state_color)
        #self.__led.blink(0.5, 0.5, on_color=(0.9,0.9,0.9), off_color=state_color)

    def _get_state_color(self, state):
        if   state == State.full:         return WaterTank.rgb_conv(0, 0, 150)
        elif state == State.normal:       return WaterTank.rgb_conv(0, 150, 0)
        elif state == State.low:          return WaterTank.rgb_conv(255, 30, 0)
        elif state == State.empty:        return WaterTank.rgb_conv(255, 0, 0)
        elif state == State.not_measured: return WaterTank.rgb_conv(0, 0, 0)
        elif state == State.sensor_error: return WaterTank.rgb_conv(255, 0, 0)
        
    def measure(self):
        if self.stop_event.is_set(): return
        result = self.__sensor.read() 
        if result[0] and result[1] and result[2]:
            self.state = State.full
            return False
        elif result[0] and result[1] and not result[2]:
            self.state = State.normal
            return False
        elif result[0] and not result[1] and not result[2]:
            self.state = State.low
            return True
        elif not result[0] and not result[1] and not result[2]:
            self.state = State.empty
            return True
        else:
            self.state = State.sensor_error
            raise Exception("Wrong sensor value measured: low: %-5s | norm: %-5s | full: %-5s!\n"\
                            "Investigate level probes physical placement "\
                            "in tank or check connection pins!"\
                            % result)

    def rgb_conv(*args):
        return tuple(1 * byte / 255 for byte in args)

    def join(self, timeout=None):
        self.stop_event.set()
        self.close()
        super().join(timeout)

    def close(self):
        self.closed = False
        if self.__valve: self.__valve.close()
        self.__sensor.close()
        self.__led.close()
        self.closed = True

    def __del__(self):
        if hasattr(self, 'closed') and not self.closed: self.close()


if __name__ == "__main__":
    probes = [12, 16, 21, 20]
    rgb_led = [17, 27, 22]
    stop_event = Event()
    try:
        tank = WaterTank(stop_event, *probes+rgb_led)
        tank.start()
        while True: sleep(0.333)
    finally:
        tank.close()
