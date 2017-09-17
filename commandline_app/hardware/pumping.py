from gpiozero import OutputDeviceBadValue
from .motor import UnidirectionMotor


class SimplePump():
    def __init__(self,
            pin,
            active_high=True,
            initial_value=0,
            frequency=200
            ):
        self._motor = UnidirectionMotor(pin, active_high, initial_value, frequency)

    def on(self):
        self._motor.on()
        #... move to consumer if loggig needed log("  Pump is fully on.")

    def off(self):
        self._motor.off()
        #... move to consumer if loggig needed log("  Pump is off.")

    def close(self):
        self._motor.close()

    def __del__(self):
        if hasattr(self, 'closed') and not self.closed:
            self.close()

    @property
    def value(self):
        return self._motor.value

    @value.setter
    def value(self, value):
        if value < 0.2:
            raise OutputDeviceBadValue("Pump speed must be higher than [0.2].")
        self._motor.value = value


class Pump(SimplePump):
    def __init__(
            self,
            pin,
            flow_pin,
            flow_vcc_pin = None,
            flow_coef = 40,
            active_high = True,
            initial_value = 0,
            frequency = 200
            ):
        super().__init__(pin, active_high, initial_value, frequency)
        self._flow_sensor = DigitalInputDevice(flow_pin)
        self._flow_sensor.when_activated =\
            self._flow_sensor.when_deactivated =\
            self.hall_pulse_volume_stop
        if flow_vcc_pin:
            self._sensor_vcc = OutputDevice(flow_vcc_pin)
        self.__reached_event = Event()
        self.flow_coef = flow_coef
        self._init_result_attributes()

    __semaphore = BoundedSemaphore(value=1) # allow one pump user at the time

    def _init_result_attributes(self):
        if self.__reached_event.is_set():
            # Log ?
            return
        self.target_value = 0
        self.pulse_count = 0
        self.time_start = None
        self.time_elaps = None

    def __handle_result(self, pump_speed):
        result = types.SimpleNamespace(
            target_value = self.target_value,
            pulse_count = self.pulse_count,
            time_start = self.time_start,
            time_elaps = self.time_elaps,
            flow_coef = self.flow_coef,
            pump_speed = pump_speed
            )
        self._init_result_attributes()
        self.__reached_event.clear()
        return result

    def pump_millilitres(self, amount, valve_device, speed=1):
        with PumpX.__semaphore:
            self.target_value = amount
            if self._sensor_vcc:
                self._sensor_vcc.on()
            self.value = speed
            valve_device.on()
            self.time_start = timer()
            self.__reached_event.wait()
            self.off()
            valve_device.off()
            if self._sensor_vcc:
                self._sensor_vcc.off()
            return self.__handle_result(speed)

    def calc_stat(self):
        pl_in_sec = self.pulse_count / self.time_elaps
        lt_in_min = pl_in_sec / self.flow_coef# Most important, it allows to calculate volume in mil/L
        ml_sec_rate = lt_in_min * (1000 / 60)
        total_vol_ml = ml_sec_rate * self.time_elaps
        return pl_in_sec, lt_in_min, ml_sec_rate, total_vol_ml

    def hall_pulse_volume_stop(self):
        self.time_elaps = timer() - self.time_start
        self.pulse_count += 1
        stats = self.calc_stat()
        if stats[3] >= self.target_value:
            self.__reached_event.set()
        if self.pulse_count % 3 == 1:
            print_on_the_fly_stats(self.pulse_count, self.time_elaps, *stats)

    def close(self):
        super().close()
        self._flow_sensor.close()
        self._sensor_vcc.close()

