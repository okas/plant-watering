if __name__ == '__main__':
    import sys
    import os
    sys.path.insert(0, os.path.abspath(__file__+'/../..'))
    from hardware.motor import UnidirectionMotor


class Pump():
    def __init__(self, pin, active_high=True, initial_value=0, frequency=100):
        self.__motor = UnidirectionMotor(
            pin,
            active_high=True,
            initial_value=0,
            frequency=100
            )
        ...


    def on(self):
        self.__motor.on()
        #... move to consumer if loggig needed log("  Pump is fully on.")

    def off(self):
        self.__motor.off()
        #... move to consumer if loggig needed log("  Pump is off.")

    def close(self):
        self.__motor.close()

    def __del__(self):
        if hasattr(self, 'closed') and not self.closed:
            self.close()

    @property
    def value(self):
        return self.__motor.value

    @value.setter
    def value(self, value):
        self.__motor.value = value
