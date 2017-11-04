* Configuration files must be valid JSON files.
* All filed are required.
* default.json.example file can e used as template to create additional files for production or development.

# Configuration spec
```
{
    "name": "default",
    "debug": false,
    "tank_args": {
        "probe_low_pin": ,
        "probe_norm_pin": ,
        "probe_full_pin": ,
        "led_low_pin": ,
        "led_norm_pin": ,
        "led_full_pin": ,
        "water_pour_time":
    },
    "pump_args": {
        "pin": ,
        "pump_speed": 1,
        "initial_value": 0,
        "frequency": 200,
        "delay_valve": 0.1,
        "flow_sensor_pin": ,
        "flow_sensor_vcc_pin":
    },
    "gardener_args": {
        "watch_cycle": 10,
        "watering_cycle": 5
    },
    "plants_args_list": [
        {
            "name": "",
            "valve_pin": ,
            "led_pin": ,
            "moist_percent": 55,
            "pour_millilitres": 50,
            "sensor_args": {
                "vcc_pin": ,
                "spi_device": ,
                "spi_channel": ,
                "dry_value": 0.875,
                "wet_value": 0.250
            }
        }
    ]
}
```
