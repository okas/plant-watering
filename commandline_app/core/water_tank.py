from time import sleep
from enum import Enum, unique
from threading import Thread, Event
from gpiozero import RGBLED
from common import common_logger as log, stoppable_sleep
from hardware import Valve

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
    __count_inst = 1
    def __init__(self,
                 stop_event,
                 watering_event,
                 tank_avail_evt,
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

        self.__devices = dict(
			low = DigitalInputDevice(probe_low_pin),
			norm = DigitalInputDevice(probe_norm_pin),
			full = DigitalInputDevice(probe_full_pin),
			led = RGBLED(led_low_pin, led_norm_pin, led_full_pin)
		)
        if valve_pin is not None:
			self.__devices['valve'] = Valve(valve_pin)
            self.__filler_thread = Thread(name="TankFiller", target=self.fill_worker)
        self.stop_event = stop_event
        self.watering_event = watering_event
        self.tank_avail_evt = tank_avail_evt
        self.fill_event = Event()
        self.standby_interval = standby_interval
        self.empty_interval = empty_interval
        self.active_interval = active_interval
        self.__state = State.not_measured
        self.last_sensor_read = None
        super().__init__(name="%s-%s" % (self.__class__.__name__, WaterTank.__count_inst))
        WaterTank.__count_inst += 1

	__state_rgb = dict(
		State.full 		   = (0, 0, 150),
		State.normal 	   = (0, 150, 0),
		State.low 		   = (255, 30, 0),
		State.empty 	   = (255, 0, 0),
		State.not_measured = (0, 0, 0),
		State.sensor_error = (255, 0, 0)
	)

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
        valve = self.__devices.get('valve')
        if valve is not None:
			self.__filler_thread.start()
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
            if valve is not None:
				self.__filler_thread.join()
            self.close()
            log("Completed Water tank watcher and filler threads.")

    def __handle_filling(self):
		valve = __devices.get('valve')
        if self.state == State.empty or (valve is not None and self.state == State.low):
            self.tank_avail_evt.clear()
        if valve is not None:
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
      
    def _change_led(self, new, old):
        state_color = Helpers.rgb_conv(__state_rgb[new])
        led = self.__devices.get('led')
        if new == State.sensor_error:
            if new == old: return
            led.blink(0.25, 0.25, on_color=state_color, off_color=(0,0,0))
            sleep(5)# FOR TESTING ONLY!!
            # TODO: Raise?
        elif self.fill_event.is_set():
            if new == old and led._blink_thread is not None: return
            self._change_filling_led(color=state_color)
        else:
            led.color = state_color

    def _change_filling_led(self, state=None, color=None):
		led = self.__devices.get('led')
        #if led._blink_thread is not None: return
        state_color = color if color is not None else Helpers.rgb_conv(__state_rgb[state])
        led.blink(0.35, 0.35, 0.15, 0.15, on_color=(0.9,0.9,0.9), off_color=state_color)
        #led.blink(0.5, 0.5, on_color=(0.9,0.9,0.9), off_color=state_color)

	def __get_levels(self):
		result = tuple(
			self.__devices(key).value for key in ['low', 'norm', 'full']
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
            raise Exception("Wrong sensor value measured: low: %-5s | norm: %-5s | full: %-5s!\n"\
                            "Investigate level probes physical placement "\
                            "at tank or check connection pins!"\
                            % is_low, is_norm, is_full)

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
		return any(device.closed for device in self.__devices)

    def close(self):
        self.closed = False
		for device in self.__devices:
			device.close()
        self.closed = True

    def __del__(self):
        if hasattr(self, 'closed') and not self.closed:
			 self.close()


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
