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
    raise Exception('Validation detected bad configuration. '\
        'Details provided in previous log messages.')


def load_configuration(config_file):
    with open(config_file) as j_file:
        ordered_config = json.load(j_file, object_pairs_hook = OrderedDict)
    try:
        validate(ordered_config)
    except:
        log.exception('Loaded Irrigation configuration is not valid! '\
            'File: %s' % config_file)
        raise
    else:
        log.debug('Loaded Irrigation configuration is valid. '\
            'File: %s' % config_file)
    return ordered_config


def store_configuration(config_file, json_content):
    try:
        validate(json_content)
    except:
        log.exception('Provided Irrigation configuration is not valid! '\
            'File: %s' % config_file)
        raise
    else:
        log.debug('Provided Irrigation configuration is valid. '\
            'File: %s' % config_file)
        with open(config_file, 'w', encoding='utf8') as outfile:
            json.dump(json_content, outfile, ensure_ascii=False, indent=4)
