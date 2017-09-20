import os
import json


def load_configuration(config_name):
    if '/' in config_name:
        file_path = config_name
    else
        file_path = os.path.abspath('%s/../%s.json' % (__file__, config_name))
    with open(file_path) as j_file:
        raw_loaded = json.load(j_file)
    return raw_loaded
