def load_cfg_prod():
    gardener_args = dict(
       pump_pin=24,
       watch_cycle=1800,
       watering_cycle=60
       )
    tank_args = dict(
       probe_low_pin=16,
       probe_norm_pin=20,
       probe_full_pin=21,
       led_low_pin=17,
       led_norm_pin=27,
       led_full_pin=22,
       water_pour_time=8
       )
    plants_args = (dict(
        id="JoodikLill",
        sensor_vcc_pin=25,
        valve_pin=18,
        led_pin=23,
        button_pin=13,
        moist_percent=55,
        watering_time=5,
        pump_power=0.3,
        device=1,
        channel=0
        ),)
    return gardener_args, tank_args, plants_args
########################################################################
def load_cfg_test1():
    gardener_args = dict(
       pump_pin=24,
       watch_cycle=10,
       watering_cycle=5
       )
    tank_args = dict(
       probe_low_pin=16,
       probe_norm_pin=20,
       probe_full_pin=21,
       led_low_pin=17,
       led_norm_pin=27,
       led_full_pin=22,
       water_pour_time=5
       )
    plants_args = (dict(
        id="JoodikLill",
        sensor_vcc_pin=25,
        valve_pin=18,
        led_pin=23,
        button_pin=13,
        moist_percent=55,
        watering_time=70,
        pump_power=1,
        device=1,
        channel=0
        ),)
    return gardener_args, tank_args, plants_args
