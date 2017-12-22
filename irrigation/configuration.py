import os
import logging
import simplejson as json
from jsonschema import Draft4Validator
from collections import OrderedDict


log = logging.getLogger(__name__)


def _load_schema():
    path = os.path.realpath(
        os.path.dirname(__file__)+'/configuration.schema'
        )
    with open(path) as s_file:
        schema = json.load(
            s_file,
            object_pairs_hook = OrderedDict,
            encoding='utf-8'
            )
    try:
        Draft4Validator.check_schema(schema)
    except SchemaError as err:
        log.exception("Irrigation configuration schema itself is bad!")
    return schema


def validate(instance):
    validator = Draft4Validator(_load_schema())
    if validator.is_valid(instance):
        return
    for err in validator.iter_errors(instance):
        log.debug(err.message)
    raise Exception()


def load_configuration(name_or_path):
    if '/' or '.json' in name_or_path:
        file_path = name_or_path
    else:
        file_path = os.path.realpath('%s/../%s.json' % (__file__, name_or_path))
    with open(file_path) as j_file:
        ordered_config = json.load(j_file, object_pairs_hook = OrderedDict)
    try:
        validate(ordered_config)
    except:
        log.exception('Loaded Irrigation configuration is not valid! '\
            'File: %s' % file_path)
    else:
        log.debug('Loaded Irrigation configuration is valid. '\
            'File: %s' % file_path)
    return ordered_config
