from sys import stdin, stdout
from time import sleep
#~ from select import select
from timeit import default_timer as timer
from signal import pause
from threading import Event, Thread
from gpiozero import OutputDevice, DigitalInputDevice
from pumping import Pump
from valve import Valve
import faulthandler

faulthandler.enable()


class DTO:
    def __init__(self, **kwargs): self.__dict__ = kwargs


class Devices():
    def __init__(self, dto, hall_pulse_cb, args):
        self.d = dto
        self.vcc = OutputDevice(args.vcc_pin)
        self.sensor = DigitalInputDevice(args.flow_pin)
        self.sensor.when_activated = hall_pulse_cb
        self.valve = Valve(args.valve_pin)
        self.pump = Pump(args.pump_pin)

    def __enter__(self): return self

    def __exit__(self, t, v, tb):
        self.sensor.when_activated = None
        self.vcc.close()
        self.sensor.close()
        self.valve.close()
        self.pump.close()


def handle_result(dto):
    try:
        a_ml = float(input("Enter milliliters: "))
        if not a_ml > 0: raise ValueError
    except:
        print("Gave '%s' as millilitres value, cannot calculate with that!" % a_ml)
        return
    time_elaps, pl_in_sec, lt_in_min, ml_sec_rate, total_vol_ml = calc_stat(dto)
    pl_in_min = pl_in_sec * 60
    ml_in_pl = total_vol_ml / dto.pulse_count
    pl_in_lt = dto.pulse_count * 1000 / total_vol_ml
    a_ml_in_pl = a_ml / dto.pulse_count
    a_ml_in_sec = a_ml / time_elaps
    a_lt_in_min = (a_ml / 1000) / (time_elaps / 60)
    a_pl_in_lt = dto.pulse_count * 1000 / a_ml
    print("===========================================================")
    print("Calculations:")
    print("  common values:")
    print("    pulses: %19d" % dto.pulse_count)
    print("    reading time (sec): %11.3f" % time_elaps)
    print("    pulses per sec: %15.3f" % pl_in_sec)
    print("    pulses per minute: %12.3f" % pl_in_min)
    print("-----------------------------------------------------------")
    print("     actual millilitre-based stats:")
    print("       total millilitres: %9.3f" % a_ml)
    print("       ml per sec: %16.3f" % a_ml_in_sec)
    print("       ml per pl: %17.3f" % a_ml_in_pl)
    print("       litres per minute: %9.3f" % a_lt_in_min)
    print("       pulses per litre: %10.3f" % a_pl_in_lt)
    print("-----------------------------------------------------------")
    print("     on-the-fly flow rate stats:")
    print("       total millilitres: %9.3f" % total_vol_ml)
    print("       ml per sec: %16.3f" % ml_sec_rate)
    print("       ml per pl: %17.3f" % ml_in_pl)
    print("       litres per minute: %9.3f" % lt_in_min)
    print("       pulses per litre: %10.3f" % pl_in_lt)
    print("===========================================================")


def handle_delayed_measuring(delay):
    if delay > 0:
        print("Waiting waterflow stopping for %s seconds:" % delay)
        for s in range(delay, 1, -1): sleep(1 if delay > 1 else delay)
    print()


def calc_stat(dto):
    time_elaps = dto.t2 - dto.t1
    pl_in_sec = dto.pulse_count / time_elaps
    lt_in_min = pl_in_sec / 15# 7.5 for single sensor state edge, 15 for both
    ml_sec_rate = lt_in_min * (1000/60)
    total_vol_ml = ml_sec_rate * time_elaps
    return time_elaps, pl_in_sec, lt_in_min, ml_sec_rate, total_vol_ml


def hall_pulse(dto, reached_event):
    dto.pulse_count += 1
    dto.t2 = timer()
    stats = (calc_stat(dto))
    if stats[4] >= dto.target_amount: reached_event.set()
    if stats[0] > 0.001: print_statistics(dto.pulse_count, *stats)
    

def print_statistics(pulse_count, time_elaps, pl_in_sec, lt_in_min, ml_sec_rate, total_vol_ml):
    s = "  -> current speed: {:.3f}L/min|{:.3f}ml/sec|{:.3f}pl/sec; vol.estim: {:.3f}ml; pulses: {}; seconds: {:.3f}."\
        .format(lt_in_min, ml_sec_rate, pl_in_sec, total_vol_ml, pulse_count, time_elaps)
    print(s, flush=True, end='\r')


def main(device_args, pump_speed=1, flow_stop_dely=0, target_amount=100):
    dto = DTO(pulse_count = 0,
              t1 = None,
              t2 = None,
              target_amount = target_amount)
    amount_reached = Event()
    #~ kbd_t = Thread(target=kbd_waiter, args=(amount_reached,), daemon=True)
    kbd_t = Thread(target=input, daemon=True)
    try:
        sensor_counter_cb = lambda: hall_pulse(dto, amount_reached)
        with Devices(dto, sensor_counter_cb, device_args) as devices:
            input("Press Enter to start measuring. To stop measuring press Enter again.")
            print("-> Starting waterflow.")
            devices.vcc.on()
            devices.valve.on()
            devices.pump.value = pump_speed
            dto.t1 = timer()
            kbd_t.start()
            while not amount_reached.wait(0.1):
                if not kbd_t.is_alive(): break
            else:
                print("\n>>> target reached: %s ml" % calc_stat(dto)[4])
            devices.pump.off()
            devices.valve.off()
            handle_delayed_measuring(flow_stop_dely)
    except KeyboardInterrupt:
        print()
        print("Keyboard exit...")
        return
    if kbd_t.is_alive():
        print(">> Press Enter to proceed...")
    if dto.pulse_count > 0: handle_result(dto)
    else: print("No pulses read!  ")
    print("End executing")


if __name__ == '__main__':
    device_args = DTO(flow_pin=6,
                      vcc_pin=25,
                      valve_pin=18,
                      pump_pin=24,
                      button_pin=13)
    process_args = dict(pump_speed=1,
                        flow_stop_dely=0,
                        target_amount=1000)
    main(device_args, **process_args)
    #~  5.21 == 1.112
    #~  18.83 == 0.868
