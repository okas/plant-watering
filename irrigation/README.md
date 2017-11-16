# Configuration files
* All configuration files must be valid JSON files.
* Do not save configs in /irrigation/ folder!
* Instead, put them near consuming application and refer them.
## Irrigation configuration
* All fields are required.
* Below is example file content, use it as template to create additional files for production or development.
* It has some sensible defaults.
### Schema
```
{
    "name": "default",
    "database_dir": "",
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
        "frequency": 100,
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

## Logging module recommended configuration
* It is used by Python's standard librarys _logging_ moduel.
* Schema: https://docs.python.org/3/library/logging.config.html#configuration-dictionary-schema
* Load it with logging.dictConfig()
* Logging module has ben set up in _irrigation_ package using recommended best practices.
### Schema
```
{
    "version": 1,
    "incremental": false,
    "disable_existing_loggers": false,
    "formatters": {
        "irrigation": {
            "class": "logging.Formatter",
            "style": "{",
            "format": "~{asctime} | {threadName} | {message}"
        }
    },
    "handlers": {
        "irrigation_console": {
            "class": "logging.StreamHandler",
            "formatter": "irrigation"
        }
    },
    "loggers": {
        "irrigation": {
            "handlers": ["irrigation_console"],
            "level": "DEBUG"
        }
    }
}
```
# Database

* Database hold info about gardeners and plants that have been watered.
* All plant measurements and waterings are recorded as well.
* Purpose is to provide machine readable data about work. Many use cases possible...

### Document database structure is like following:
```
{
    "gardener_instances": [
        {
        "__id": <int>,
            "uuid1": "uuid1()",
            "watch_cycle": <float>,
            "watering_cycle": <float>,
            "plants": [
                {
            "uuid1": "uuid1()",
                    "name": "",
                    "moist_level": <float>
                }
            ]
        }
    ],
    "plant_moistures": [
        {
            "gardener__id": <gardener_instances__id>,
            "plant_uuid1": <parent plant>,
            "ts_utc": "timestamp()",
            "percent": <float>
        }
    ],
    "plant_waterings": [
        {
            "gardener__id": <gardener_instances__id>,
            "plant_uuid1": <parent plant>,
            "ts_utc": "timestamp()",
            "mil_lit": <float>
        }
    ]
}
```
