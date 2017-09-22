from time import sleep
from types import SimpleNamespace
from timeit import default_timer as timer
from threading import Event
from gpiozero import DigitalInputDevice, OutputDevice
from .motor import UnidirectionMotor


class Pump(UnidirectionMotor):
    def __init__(
            self,
            pin,
            flow_sensor_pin,
            flow_sensor_vcc_pin = None,
            flow_coef = 40,
            active_high = True,
            initial_value = 0,
            frequency = 100,
            delay_motor = None
            ):
        super().__init__(pin, active_high, initial_value, frequency)
        self._flow_sensor = DigitalInputDevice(flow_sensor_pin)
        if flow_sensor_vcc_pin:
            self._sensor_vcc = OutputDevice(flow_sensor_vcc_pin)
        self.reached_event = Event()
        self._delay = delay_motor
        self.flow_coef = flow_coef
        self.__reset_state()

    def __reset_state(self):
        self.time_elaps   = 0
        self.time_start   = 0
        self.pulse_count  = 0
        self.target_value = 0
        self._flow_sensor.when_activated     = None
        self._flow_sensor.when_deactivated   = None

    def __set_flow_sensor(self):
        self._flow_sensor.when_activated   = self.__hall_pulse_volume_stop
        self._flow_sensor.when_deactivated = self.__hall_pulse_volume_stop

    def __hall_pulse_volume_stop(self):
        self.time_elaps = timer() - self.time_start
        self.pulse_count += 1
        stats = self.calc_stat()
        if stats[0] >= self.target_value:
            self.reached_event.set()

    def __handle_result(self, pump_speed):
        stats = self.calc_stat()
        result = SimpleNamespace(
            target_value = self.target_value,
            pulse_count = self.pulse_count,
            time_elaps = self.time_elaps,
            flow_coef = self.flow_coef,
            pump_speed = pump_speed,
            total_vol_ml = stats[0],
            pl_in_sec = stats[1],
            lt_in_min = stats[2],
            ml_sec_rate = stats[3]
            )
        self.__reset_state()
        self.reached_event.clear()
        return result

    def pump_millilitres(self, amount, valve_device, speed=1):
        self.target_value = amount
        self.__set_flow_sensor()
        if self._sensor_vcc:
            self._sensor_vcc.on()
        self.value = speed
        if self._delay:
            sleep(self._delay)
        valve_device.on()
        self.time_start = timer()
        self.reached_event.wait()
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
        return total_vol_ml, pl_in_sec, lt_in_min, ml_sec_rate

    def close(self):
        super().close()
        if hasattr(self, '_flow_sensor'):
            self._flow_sensor.close()
        if hasattr(self, '_sensor_vcc'):
            self._sensor_vcc.close()

    def __del__(self):
        self.close()
