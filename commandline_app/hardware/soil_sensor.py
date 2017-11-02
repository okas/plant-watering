from time import sleep
from timeit import default_timer as timer
from statistics import median
from gpiozero import MCP3008, OutputDevice
import sys
import os
sys.path.insert(1, os.path.abspath(__file__+'/../..'))
from common import common_logger as log


class CapacitiveSensor():
    def __init__(
            self,
            vcc_pin,
            spi_device,
            spi_channel,
            dry_value,
            wet_value,
            measuring_samples=40):
        self.closed = False
        self.__spi_dev = MCP3008(device = spi_device, channel = spi_channel)
        self.__spi_vcc = OutputDevice(vcc_pin)#using GPIO pin to power the Sensor!
        self.dry_value = dry_value
        self.wet_value = wet_value
        self.samples = measuring_samples

    def __del__(self):
        if not self.closed:
            self.close()

    def __read_iter(self, samples = None):
        for i in range(samples or self.samples):
            sleep(0.01)
            v = self.__spi_dev.value
            yield v

    def calibrate_dry(self, samples = None):
        self.dry_value = median(self.read_samples(samples))

    def calibrate_wet(self, samples = None):
        self.wet_value = median(self.read_samples(samples))

    def read_samples(self, samples = None) -> list:
        self.__spi_vcc.on()
        sleep(0.2)
        values = list(self.__read_iter(samples))
        self.__spi_vcc.off()
        return values

    @property
    def moisture_percent(self) -> float:
        t1 = timer()
        readings = self.read_samples()
        t2 = timer()
        elaps = t2 - t1
        v = median(readings)
        ratio = (v - self.wet_value) / (self.dry_value - self.wet_value)
        result_ratio_inversed_rounded = round((1 - ratio) * 100, 2)
        log("  Sensor moisture median: [{}%], {:d} samples in {:.3f} seconds)."\
            .format(result_ratio_inversed_rounded, len(readings), elaps))
        return result_ratio_inversed_rounded

    def close(self):
        self.__spi_dev.close()
        self.__spi_vcc.close()
        self.closed = True
