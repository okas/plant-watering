import sys
import os
import argparse
from types import SimpleNamespace
from timeit import default_timer as timer
from time import sleep
from threading import Event, BoundedSemaphore
from functools import partial
from gpiozero import OutputDevice, DigitalInputDevice
import faulthandler
sys.path.insert(0, os.path.abspath(__file__+'/../..'))
from hardware import Pump


faulthandler.enable()


def print_result(
        a_ml,
        mode,
        edges,
        target_value,
        pulse_count,
        time_elaps,
        flow_coef,
        pump_speed,
        total_vol_ml,
        pl_in_sec,
        lt_in_min,
        ml_sec_rate
        ):
    pl_in_min = pl_in_sec * 60
    ml_in_pl = total_vol_ml / pulse_count
    pl_in_lt = pulse_count * 1000 / total_vol_ml
    a_ml_in_pl = a_ml / pulse_count
    a_ml_in_sec = a_ml / time_elaps
    a_lt_in_min = (a_ml / 1000) / (time_elaps / 60)
    a_pl_in_lt = pulse_count * 1000 / a_ml
    totals = [a_ml, total_vol_ml]
    ml_per_sec = [a_ml_in_sec, ml_sec_rate]
    ml_per_pl = [a_ml_in_pl, ml_in_pl]
    lt_per_min = [a_lt_in_min, lt_in_min]
    pl_per_lt = [a_pl_in_lt, pl_in_lt]
    for x in (totals, ml_per_sec, ml_per_pl, lt_per_min, pl_per_lt):
        x += [totals[1] - totals[0]]
        x += [100 * x[2] / totals[0]]
    print("=" * 74)
    print("Calculations:")
    print("  common values:")
    print("    mode: %19s" % mode)
    print("    edges: %18s\n" % edges)
    print("    pulses: %17d" % pulse_count)
    print("    reading time (sec): %10.4f" % time_elaps)
    print("    pulses per sec: %14.4f" % pl_in_sec)
    print("    pulses per minute: %11.4f" % pl_in_min)
    print("    volume target (mil): %9.4f" % target_value)
    print("    flow coefficient: %12.4f" % flow_coef)
    print("    pump speed: %18.4f\n" % pump_speed)
    print("  rate statistics:        [actual] |  [reading] | [diff.val] |   [diff. %]")
    print("    total ml: %20.4f | %10.4f | %10.4f | %10.4f%%" % tuple(totals))
    print("    ml per sec: %18.4f | %10.4f | %10.4f | %10.4f%%" % tuple(ml_per_sec))
    print("    ml per pl: %19.4f | %10.4f | %10.4f | %10.4f%%" % tuple(ml_per_pl))
    print("    litres per minute: %11.4f | %10.4f | %10.4f | %10.4f%%" % tuple(lt_per_min))
    print("    pulses per litre: %12.4f | %10.4f | %10.4f | %10.4f%%" % tuple(pl_per_lt))
    print("=" * 74)


def hall_pulse_time_stop(dto, reached_event):
    '''testing...'''
    dto.time_elaps = timer() - dto.time_start
    dto.pulse_count += 1
    stats = calc_stat(dto)
    if dto.time_elaps >= dto.target_value:
        reached_event.set()
    if dto.pulse_count % 5 == 0:
        print_on_the_fly_stats(dto.pulse_count, dto.time_elaps, *stats)


def hall_pulse_count_stop(dto, reached_event):
    '''testing...'''
    dto.time_elaps = timer() - dto.time_start
    dto.pulse_count += 1
    const_ml_in_pl = 0.4136
    # get ceiling, because measurement and code here has time diff.
    ml_now = const_ml_in_pl * dto.pulse_count
    pl_sec = dto.pulse_count / dto.time_elaps
    ml_sec = ml_now / dto.time_elaps
    target_pulses = dto.target_value / const_ml_in_pl
    #if ml_now >= dto.target_value:
    if dto.pulse_count >= target_pulses:
        reached_event.set()
    if dto.pulse_count % 2 == 1:
        print_on_the_fly_stats(
            dto.pulse_count,
            dto.time_elaps,
            pl_sec,
            ml_sec / (1000 / 60),
            ml_sec,
            ml_now
            )


def print_on_the_fly_stats(
        pulse_count,
        time_elaps,
        total_vol_ml,
        pl_in_sec,
        lt_in_min,
        ml_sec_rate,
        ):
    s = "-> current speed: {:.3f}L/min|{:.3f}ml/sec|{:.3f}pl/sec||"\
        "vol.estim: {:.3f}ml; pulses: {}; seconds: {:.3f}"\
        .format(lt_in_min, ml_sec_rate, pl_in_sec, total_vol_ml, pulse_count, time_elaps)
    print(s, flush=True, end='\r')


def main(
    mode,
    pump_speed,
    target_value,
    device_args,
    single_edge,
    flow_coefficient=None
    ):
    dto = SimpleNamespace(
        mode = mode,
        edges = 'single' if single_edge else 'both',
        )
    valve = OutputDevice(device_args.valve_pin)
    pump = Pump(
        device_args.pump_pin,
        device_args.flow_pin,
        device_args.vcc_pin,
        flow_coefficient,
        frequency = 200
        )
    if mode in ('time', 'pulse'):
        raise NotImplementedError
        mode_callbacks = dict(
        time = hall_pulse_time_stop,
        pulse = hall_pulse_count_stop
        )
        cb_args = (dto, amount_reached)
        if dto.edges == 'single':
            pump._flow_sensor.when_activated = mode_callbacks[mode]
        else:
            pump._flow_sensor.when_deactivated = mode_callbacks[mode]
    elif dto.edges == 'single':
        raise NotImplementedError
        pump._flow_sensor.when_deactivated = None
    try:
        input("Press Enter to start measuring.\n"\
              "   To stop measuring press Enter again "\
              "or wait for target value [%s] fulfillment.\n"\
              "   Mode: [%s]; single edge: [%s]; flow coefficient: [%s]; "\
              "pump speed: [%s]."\
              % (target_value, mode, single_edge, flow_coefficient, pump_speed))
        print("\nStarting waterflow.")
        stats = pump.pump_millilitres(target_value, valve, pump_speed)
    except KeyboardInterrupt:
        print("\nKeyboard exit...")
        return
    finally:
        valve.close()
        pump.close()
    if stats.pulse_count <= 0:
        print("\nNo pulses read!")
        return
    sleep(0.1)
    print("\n>>>> target reached: %.4f ml" % stats.target_value)
    actual_value = input("Enter actual milliliters: ")
    try:
        actual_value = float(actual_value)
    except ValueError:
        print("Erroneus value or empty response: [%s]!" % actual_value)
    else:
        stats.__dict__.update(dto.__dict__) #Modifying dict, because in test it is not needed any more!
        print_result(actual_value, **stats.__dict__)
    print()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Test program to interact waterflow sensor and get calculations.'
        )
    parser.add_argument(
        '-m', '--mode',
        default='volume',
        choices=('volume', 'time', 'pulse'),
        required=False,
        help="Default is [%(default)s]. [volume] means TARGET is millilitres. "\
             "[time] means TARGET is seconds. [pulse] means TARGET is millilitres, "\
             "but work will be stopped by millilitres value."
        )
    parser.add_argument(
        '-t', '--target',
        default=100,
        type=float,
        required=False,
        help="Default is [%(default)s]. Target value to pump and measure. "\
             "If it's reached then pump stops automatically. "\
             "It works accordingly to selected MODE."
        )
    parser.add_argument(
        '-c', '--flow-coefficient',
        default=40,
        type=float,
        required=False,
        help="Default is [%(default)s]. It is used only if MODE is [volume]. "\
             "To calculate current flow rate. "\
             "Used in formula: [litres per minute] = [pulses per second] / [coefficient]. "\
             "NB! Hardly related to flow rate sonsor properties!"
        )
    parser.add_argument(
        '-s', '--single-edge',
        action='store_true',
        required=False,
        help="Specifiest that water flow sensor single edge must be listened. "\
             "Otherwize both edges are used. " \
             "Consider [FLOW-COEFFICIENT] value, it is used in interrupt!"
        )
    parser.add_argument(
        '-p', '--pump-speed',
        default=1,
        type=float,
        required=False,
        help="Default is [%(default)s]. Value between 0.2-1. "\
             "Lower than 0.3 causes lot of inaccuracy in calculations "\
             "and pump won't also run smoothly."
        )
    args = parser.parse_args()
    device_args = SimpleNamespace(
        flow_pin=26,
        vcc_pin=19,
        valve_pin=18,
        pump_pin=24,
        button_pin=13
    )
    main(
        args.mode,
        args.pump_speed,
        args.target,
        device_args,
        args.single_edge,
        args.flow_coefficient,
    )
