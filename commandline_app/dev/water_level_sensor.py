from time import sleep
from datetime import datetime
from gpiozero import InputDevice, OutputDevice, MCP3008
from threading import BoundedSemaphore
#from common import common_logger as log


class LevelSensor:                                                                                              
    __read_semaphore = BoundedSemaphore(value=1) # we have singel watertank in system
    
    def __init__(self,
                 probe_vcc_pin,
                 probe_low_pin,
                 probe_norm_pin,
                 probe_full_pin):
        #~ self.__probe_vcc = OutputDevice(probe_vcc_pin)
        self.__low = InputDevice(probe_low_pin, pull_up=True)
        #~ self.__low = MCP3008(0, device=1)
        self.__norm = InputDevice(probe_norm_pin, pull_up=True)
        #~ self.__norm = MCP3008(1, device=1)
        self.__full = InputDevice(probe_full_pin, pull_up=True)
        #~ self.__full = MCP3008(2, device=1)
        self.last_read = None

    def read(self):
        if self.closed:
            log("LevelSensor probes already closed!")
            return
        with LevelSensor.__read_semaphore:
            #self.__probe_vcc.on()
            result = (self.__low.value, self.__norm.value, self.__full.value)
            #self.__probe_vcc.off()
        self.last_read = datetime.now()
        print("  Sensor value: low: %-5s | norm: %-5s | full: %-5s" % result)
        return result

    @property
    def closed(self):
        #~ return self.__probe_vcc.closed\
               #~ or self.__low.closed\
               #~ or self.__norm.closed\
               #~ or self.__full.closed
        return self.__low.closed\
               or self.__norm.closed\
               or self.__full.closed
    
    def close(self):
        #self.__probe_vcc.close()
        self.__low.close()
        self.__norm.close()
        self.__full.close()

    def __del__(self):
        if hasattr(self, 'closed') and not self.closed: self.close()


if __name__ == '__main__':
    probes = dict(probe_vcc_pin=26,
                   probe_low_pin=16,
                   probe_norm_pin=20,
                   probe_full_pin=21)
    __sensor = LevelSensor(**probes)
    
    try:
        while True:
            result = __sensor.read()
            sleep(0.2)
    finally:
        __sensor.close()
