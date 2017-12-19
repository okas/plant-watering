import os
import json
from collections import OrderedDict


def load_configuration(name_or_path):
    if '/' or '.json' in name_or_path:
        file_path = name_or_path
    else:
        file_path = os.path.realpath(
            '{}/../{}.json'.format(__file__, name_or_path)
            )
    with open(file_path) as j_file:
        ordered_config = json.load(j_file, object_pairs_hook = OrderedDict)
    return ordered_config
