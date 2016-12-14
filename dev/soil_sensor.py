from gpiozero import MCP3008, OutputDevice
from time import sleep
from datetime import datetime
from statistics import median

sensor1 = MCP3008(channel=0, device=1)    
vcc = OutputDevice(25, initial_value=False)

vref = 3.3
val_max = 0.782
vref_raw_max = 800

#vmax = 2.53
# 0.28 sisse GND
# 0.33 Vcc
# 0.05 Vout
#R = 10
#I = 0.33

def calcMoisturePercent(value):
    return 100 * value / val_max

def calcVoltage(bitValue):
    return (bitValue * vref) / 1023

format_s = "reading: {0:.1f}; voltage: {1:.4f}V; moisture level is {2:.2f}%."
median_range = 100

try:
    while True:
        volts = []
        moists = []
        readings = []
        vcc.on()
        sleep(1.5)
        for i in range(median_range):
            readings.append(sensor1.raw_value)
            moists.append(calcMoisturePercent(sensor1.value))
            volts.append(calcVoltage(readings[i]))
            if (i + 1) % 10 == 0:
                print(format_s.format(readings[i], volts[i], moists[i]), flush=True, end='\r')
            
            sleep(0.01)
        m_volt = median(volts)
        m_read = median(readings)
        m_moist = median(moists)
        print("At {1}, medians of last {0} values: {2}"\
              .format(median_range,
                      datetime.now().isoformat(),
                      format_s.format(m_read, m_volt, m_moist)))
        vcc.off()
        #sleep(0.5)
finally:
    sensor1.close()
    vcc.close()
