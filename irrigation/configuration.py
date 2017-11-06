import os
import json
from collections import namedtuple


def recursive_converter(obj):
    if isinstance(obj, dict):
        for key, val in obj.items():
            obj[key] = recursive_converter(val)
        return namedtuple('GenericConfig', obj.keys())(**obj)
    elif isinstance(obj, list):
        return [recursive_converter(item) for item in obj]
    else:
        return obj


def load_configuration(name_or_path):
    if '/' or '.json' in name_or_path:
        file_path = name_or_path
    else:
        file_path = os.path.abspath('%s/../%s.json' % (__file__, name_or_path))
    with open(file_path) as j_file:
        config = json.load(j_file, object_hook = recursive_converter)
    return config
