import gpiozero
from time import sleep
from signal import pause

btn_toggle = gpiozero.Button(13)
pump = gpiozero.Motor(24, 23)

def toggle_pump():
    print("Pump is going to", "stop." if  pump.is_active else "start.")
    if pump.is_active:
        pump.stop()
    else:
        pump.forward(1)

btn_toggle.when_pressed = toggle_pump
pause()

