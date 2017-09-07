from timeit import default_timer as timer
from threading import Event
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
        self.sensor.when_activated =\
            self.sensor.when_deactivated =\
            hall_pulse_cb
        self.valve = Valve(args.valve_pin)
        self.pump = Pump(args.pump_pin
        )

    def __enter__(self):
        return self

    def __exit__(self, t, v, tb):
        self.vcc.close()
        self.sensor.close()
        self.valve.close()
        self.pump.close()


def handle_result(dto, a_ml):
    time_elaps, pl_in_sec, lt_in_min, ml_sec_rate, total_vol_ml = calc_stat(dto)
    pl_in_min = pl_in_sec * 60
    ml_in_pl = total_vol_ml / dto.pulse_count
    pl_in_lt = dto.pulse_count * 1000 / total_vol_ml
    a_ml_in_pl = a_ml / dto.pulse_count
    a_ml_in_sec = a_ml / time_elaps
    a_lt_in_min = (a_ml / 1000) / (time_elaps / 60)
    a_pl_in_lt = dto.pulse_count * 1000 / a_ml
    totals = [a_ml, total_vol_ml]
    ml_per_sec = [a_ml_in_sec, ml_sec_rate]
    ml_per_pl = [a_ml_in_pl, ml_in_pl]
    lt_per_min = [a_lt_in_min, lt_in_min]
    pl_per_lt = [a_pl_in_lt, pl_in_lt]
    for x in totals, ml_per_sec, ml_per_pl, lt_per_min, pl_per_lt:
        x += [totals[0] - totals[1]]
        x += [100 * x[2] / totals[1]]
    print("===========================================================")
    print("Calculations:")
    print("  common values:")
    print("    pulses: %19d" % dto.pulse_count)
    print("    reading time (sec): %11.3f" % time_elaps)
    print("    pulses per sec: %15.3f" % pl_in_sec)
    print("    pulses per minute: %12.3f" % pl_in_min)
    print("-----------------------------------------------------------")
    print("     rate statistics:")
    print("       [article]           [actual] | [reading] | [dif.val] | [diff. % ]")
    print("       total millilitres: %9.3f | %9.3f | %9.3f | %9.3f%%" % tuple(totals))
    print("       ml per sec: %16.3f | %9.3f | %9.3f | %9.3f%%" % tuple(ml_per_sec))
    print("       ml per pl: %17.3f | %9.3f | %9.3f | %9.3f%%" % tuple(ml_per_pl))
    print("       litres per minute: %9.3f | %9.3f | %9.3f | %9.3f%%" % tuple(lt_per_min))
    print("       pulses per litre: %10.3f | %9.3f | %9.3f | %9.3f%%" % tuple(pl_per_lt))
    print("===========================================================")

def calc_stat(dto):
    time_elaps = dto.t2 - dto.t1
    pl_in_sec = dto.pulse_count / time_elaps
    lt_in_min = pl_in_sec / 40.05# 7.5 for single sensor state edge, 15 for both
    ml_sec_rate = lt_in_min * (1000/60)
    total_vol_ml = ml_sec_rate * time_elaps
    return time_elaps, pl_in_sec, lt_in_min, ml_sec_rate, total_vol_ml

def hall_pulse(dto, reached_event):
    dto.pulse_count += 1
    dto.t2 = timer()
    stats = (calc_stat(dto))
    if stats[4] >= dto.target_amount:
        reached_event.set()
    if stats[0] > 0.001:
        print_on_the_fly_stats(dto.pulse_count, *stats)

def print_on_the_fly_stats(
        pulse_count,
        time_elaps,
        pl_in_sec,
        lt_in_min,
        ml_sec_rate,
        total_vol_ml
        ):
    s = "  -> current speed: {:.3f}L/min|{:.3f}ml/sec|{:.3f}pl/sec; "\
        "vol.estim: {:.3f}ml; pulses: {}; seconds: {:.3f}."\
        .format(lt_in_min, ml_sec_rate, pl_in_sec, total_vol_ml, pulse_count, time_elaps)
    print(s, flush=True, end='\r')


def main(device_args, pump_speed=1, flow_stop_dely=0, target_amount=100):
    dto = DTO(
        pulse_count = 3,
        t1 = None,
        t2 = None,
        target_amount = target_amount
        )
    amount_reached = Event()
    try:
        with Devices(
                dto,
                lambda: hall_pulse(dto, amount_reached),
                device_args
                ) as devices:
            input("Press Enter to start measuring.\n"\
                  "   To stop measuring press Enter again\n"\
                  "   or wait for target amount [%s]." % target_amount)
            print("\n-> Starting waterflow.")
            devices.pump.value = pump_speed
            devices.vcc.on()
            devices.valve.on()
            dto.t1 = timer()
            amount_reached.wait()
            devices.valve.off()
            devices.pump.off()
            devices.vcc.off()
            print("\n>>> target reached: %s ml" % calc_stat(dto)[4])
    except KeyboardInterrupt:
        print("\nKeyboard exit...")
        return
    if dto.pulse_count <= 0:
        print("No pulses read!")
        return
    a_ml = float(input("Enter actual milliliters: "))
    if a_ml is None:
        print("You didn't gave any value!")
    elif a_ml <= 0:
        print("Gave [%s] as millilitres value, cannot calculate with that!" % a_ml)
    else:
        handle_result(dto, a_ml)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Test program to interact waterflow sensor and get calculations.'
        )
    parser.add_argument(
        '-ta', '--targetamount',
        default=100,
        type=float,
        required=False,
        help="Default is [%(default)s]. Target amount to pump andm measure. "\
              "If it's reached then pumping stops automatically."
        )
    target_amount = parser.parse_args().targetamount

    device_args = DTO(
        flow_pin=26,
        vcc_pin=19,
        valve_pin=18,
        pump_pin=24,
        button_pin=13
    )
    process_args = dict(
        pump_speed=1,
        flow_stop_dely=0,
        target_amount=target_amount or 100
    )
    main(device_args, **process_args)
    print("End executing")
