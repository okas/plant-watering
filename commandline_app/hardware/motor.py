from gpiozero import OutputDevice, OutputDeviceBadValue


class UnidirectionMotor(OutputDevice):
    """
    Generic output device configured for pulse-width modulation (PWM).

    :param int pin:
        The GPIO pin which the device is attached to. See :ref:`pin_numbering`
        for valid pin numbers.

    :param bool active_high:
        If ``True`` (the default), the :meth:`on` method will set the GPIO to
        HIGH. If ``False``, the :meth:`on` method will set the GPIO to LOW (the
        :meth:`off` method always does the opposite).

    :param float initial_value:
        If ``0`` (the default), the device's duty cycle will be 0 initially.
        Other values between 0 and 1 can be specified as an initial duty cycle.
        Note that ``None`` cannot be specified (unlike the parent class) as
        there is no way to tell PWM not to alter the state of the pin.

    :param int frequency:
        The frequency (in Hz) of pulses emitted to drive the device. Defaults
        to 100Hz.
    """
    def __init__(self, pin, active_high=True, initial_value=0, frequency=100):
        if not 0 <= initial_value <= 1:
            raise OutputDeviceBadValue("initial_value must be between 0 and 1")
        super().__init__(pin, active_high, initial_value=None)
        try:
            # XXX need a way of setting these together
            self.pin.frequency = frequency
            self.value = initial_value
        except:
            self.close()
            raise

    def _state_to_value(self, state):
        return float(state if self.active_high else 1 - state)

    def _value_to_state(self, value):
        return float(value if self.active_high else 1 - value)

    def _write(self, value):
        if not 0 <= value <= 1:
            raise OutputDeviceBadValue("PWM value must be between 0 and 1")
        super()._write(value)

    def on(self):
        self._write(1)

    def off(self):
        self._write(0)

    def toggle(self):
        """
        Toggle the state of the device. If the device is currently off
        (:attr:`value` is 0.0), this changes it to "fully" on (:attr:`value` is
        1.0).  If the device has a duty cycle (:attr:`value`) of 0.1, this will
        toggle it to 0.9, and so on.
        """
        self.value = 1 - self.value

    def close(self):
        try:
            self.pin.frequency = None
        except AttributeError:
            # If the pin's already None, ignore the exception
            pass
        super().close()

    @property
    def value(self):
        """
        The duty cycle of the PWM device. 0.0 is off, 1.0 is fully on. Values
        in between may be specified for varying levels of power in the device.
        """
        return self._read()

    @value.setter
    def value(self, value):
        self._write(value)

    @property
    def is_active(self):
        """
        Returns ``True`` if the device is currently active (:attr:`value` is
        non-zero) and ``False`` otherwise.
        """
        return self.value != 0

    @property
    def frequency(self):
        """
        The frequency of the pulses used with the PWM device, in Hz. The
        default is 100Hz.
        """
        return self.pin.frequency

    @frequency.setter
    def frequency(self, value):
        self.pin.frequency = value
