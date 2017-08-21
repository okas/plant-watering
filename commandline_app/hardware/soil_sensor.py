from gpiozero import PWMLED, MCP3008, OutputDevice
from time import sleep, time
from statistics import median
from common import common_logger as log

class SoilSensor():
    # Excpecting chip's Vdd +5V
    # todo: calculate spi value specifics based on voltages that consumer can provide

    # At the most moistured soli values are as following:
    # - soil moisture sensor 3V3; 0.33A; sensor resistance is about R10 (lowest)
    __val_max = 0.782
    __vref = 3.3
    __vref_raw_max = 800

    def __init__(self, vcc_pin, reads=250, wait_for_seconds=0.01, **spi_args):
        self.__spi_args = spi_args
        self.__spi_dev = MCP3008(**spi_args)
        self.__spi_vcc = OutputDevice(vcc_pin)#using GPIO pin to power the Sensor!
        self.reads = reads
        self.wait_for_seconds = wait_for_seconds

    @property
    def moisture_percent(self):
        result = 100 * median(self.read()) / SoilSensor.__val_max
        log("  Sensor moisture median: {:.2f}%.".format(result))
        return result

    '''
    Multiple readigns are usuallt better. Calculate some avarag or median out of list of results
    :param int reads:
        Times to read sensor.
    :param float wait_for_seconds:
        Waiting time between reads.
    '''
    def read(self):
        log("  Sensor is on.")
        values =[]
        t1 = time()
        self.__spi_vcc.on()
        values = [i for i in self.__read_iter()]
        self.__spi_vcc.off()
        t2 = time()
        log("  Sensor is off; read {:d} values in {:.3f} seconds.".format(self.reads, (t2 - t1)))
        return values

    def __read_iter(self):
        for i in range(self.reads):
            v = self.__spi_dev.value
            sleep(self.wait_for_seconds) 
            yield v

    def close(self):
        self.closed = False
        self.__spi_dev.close()
        self.__spi_vcc.close()
        self.closed = True

    def __del__(self):
        if hasattr(self, 'closed') and not self.closed: self.close()
