from gpiozero import OutputDevice
from common import common_logger as log

class Valve(OutputDevice):
    def on(self):
        super().on()
        log("  Valve is on.")
        
    def off(self):
        super().off()
        log("  Valve is off.")
