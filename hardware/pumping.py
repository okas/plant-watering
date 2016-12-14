from common import common_logger as log
from hardware import UnidirectionMotor


class Pump(UnidirectionMotor):
    @property
    def value(self): return super().value
    
    @value.setter
    def value(self, value):
        # todo: runtime sets to default value during init?
        super(Pump, self.__class__).value.fset(self, value)
        log("  Pump is on at power '{:.3f}'.".format(value))

    def on(self):
        super().on()
        log("  Pump is fully on.")
        
    def off(self):
        super().off()
        log("  Pump is off.")

    def close(self):
        super().close()

    def __del__(self):
        if hasattr(self, 'closed') and not self.closed: self.close()
