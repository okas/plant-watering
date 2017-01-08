from RPi import GPIO
from time import sleep, time
from signal import pause
from threading import Event
from gpiozero import Button
from pumping import Pump


pulse_count = 0
stop_evt = Event()
button = None
pump = None
t1 = t2 = None


def hall_pulse(channel):
    global pulse_count, t2
    pulse_count += 1
    t2 = time()
    work_time = t2 - t1
    print("current speed: %.3f pl/sec; pulses: %d"\
        % (pulse_count/work_time, pulse_count), flush=True, end='\r')


def button_pressed(btn):
    if pump.is_active: stop_evt.set()
    else: stop_evt.clear()


def setup_gpio(flow_pin, button_pin, pump_pin):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(flow_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(flow_pin, GPIO.RISING, callback=hall_pulse, bouncetime=50)
    global button, pump
    button = Button(button_pin)
    button.when_pressed = button_pressed
    pump = Pump(pump_pin)


def handle_result():
    ml = float(input("Enter milliliters: "))
    if not ml > 0:
        print("Gave '%s' as millilitres value, cannot calculate with that!" % ml)
        return
    work_time = t2 - t1
    ml_per_pl = ml / pulse_count
    ml_in_sec = ml / work_time
    l_in_min = (ml / 1000) / (work_time / 60)
    pl_in_sec = pulse_count / work_time
    pl_in_min = pulse_count / (work_time / 60)
    print("===========================================================\nCalculations:")
    print("  given values:")
    print("    pulses: %18d" % pulse_count)
    print("    reading time (sec): %6.3f" % work_time)
    print("    millilitres: %13.3f" % ml)
    print("-----------------------------------------------------------")
    print("      waterflow: %.3f ml/p = %.3f ml / %d pulses" % (ml_per_pl, ml, pulse_count))
    print("      ml per sec: %16.3f" % ml_in_sec)
    print("      pl per sec: %16.3f" % pl_in_sec)
    print("      litres per minute: %9.3f" % l_in_min)
    print("      pulses per minute: %9.3f" % pl_in_min)
    print("===========================================================")

    
def main(flow_pin, button_pin, pump_pin):
    global t1
    try:
        setup_gpio(flow_pin, button_pin, pump_pin)
        print("Push the button to start executing")
        button.wait_for_press()
        print("-> Starting waterflow.")
        pump.on()
        t1 = time()
        stop_evt.wait()
        pump.off()
        wait_for = 4
        print("Waiting waterflow stopping for %s seconds:" % wait_for)
        for s in range(wait_for, 1, -1):
            #~ print("%s seconds left..." % s, flush=True, end='\r')
            sleep(1 if wait_for > 1 else wait_for)
        print()
    except KeyboardInterrupt:
        print("Exiting gracefully...")
    else:
        if pulse_count > 0: handle_result()
        else: print("No pulses read!  ")    
    finally:
        GPIO.remove_event_detect(flow_pin)
        GPIO.cleanup((flow_pin, button_pin, pump_pin))
    print("End executing")


if __name__ == '__main__':
    main(6, 13, 24)

