from ._version import __version__

import sys
import logging
from .gardener import Gardener
from .configuration import load_configuration


logging.getLogger(__name__).addHandler(logging.NullHandler())


LOGGER_CONFIG = dict(
    style = '{',
    format = '{asctime} | {threadName} | {message}'
    )


def run_and_return_by_conf_path(config_path):
    cfg = load_configuration(config_path)
    return Gardener(cfg)


def run_and_return_by_conf_obj(config):
    return Gardener(config)


__all__ = [
    '__version__',
    'Gardener',
    'load_configuration',
    'run_and_return',
    'LOGGER_CONFIG'
    ]
