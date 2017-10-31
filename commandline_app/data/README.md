# placeholder folder for statistis of plant waterings
# using unqlite database: https://unqlite.org/index.html

# database structure:
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
    "plant_moisture_measurements": [
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
