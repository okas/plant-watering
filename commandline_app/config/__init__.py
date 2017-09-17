import os
import json


def ___json_file_loader(file_name):
    if '/' not in file_name:
        file_name = os.path.abspath('%s/../%s.json' % (__file__, file_name))
    with open(file_name) as j_file:
        raw_loaded = json.load(j_file)
    return raw_loaded

def load_configuration(config_name):
    raw_config = ___json_file_loader(config_name)
    return (
        raw_config['gardener_args'],
        raw_config['pump_args'],
        raw_config['tank_args'],
        raw_config['plants_args']
        )
