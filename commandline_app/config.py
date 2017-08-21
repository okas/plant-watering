def load_cfg_prod():
    gardener_args = dict(pump_pin=24, watch_cycle=1800, watering_cycle=60)
    tank_args = dict(probe_vcc_pin=26,
                     probe_low_pin=16,
                     probe_norm_pin=20,
                     probe_full_pin=21,
                     led_low_pin=17,
                     led_norm_pin=27,
                     led_full_pin=22,
                     valve_pin=None)
    plants_args = (
        dict(id="JoodikLill",
             sensor_vcc_pin=25,
             valve_pin=23,
             led_pin=18,
             button_pin=13,
             moist_percent=55,
             watering_time=5,
             pump_power=0.3,
             device=1),
        )
    return gardener_args, tank_args, plants_args
########################################################################
def load_cfg_test1():
    gardener_args = dict(pump_pin=24, watch_cycle=25, watering_cycle=15)
    tank_args = dict(probe_vcc_pin=26,
                     probe_low_pin=16,
                     probe_norm_pin=20,
                     probe_full_pin=21,
                     led_low_pin=17,
                     led_norm_pin=27,
                     led_full_pin=22,
                     valve_pin=None,
                     standby_interval=12,
                     empty_interval=5)
    plants_args = (
        dict(id="JoodikLill",
             sensor_vcc_pin=25,
             valve_pin=23,
             led_pin=18,
             button_pin=13,
             moist_percent=55,
             watering_time=5,
             pump_power=0.25,
             device=1),
        )
    return gardener_args, tank_args, plants_args
