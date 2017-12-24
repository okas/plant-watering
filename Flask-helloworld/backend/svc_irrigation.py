import os
import sys
import logging
from contextlib import suppress
from flask import current_app, json

sys.path.insert(1, os.path.dirname(sys.path[0]))
import irrigation


log = logging.getLogger(__name__)

__instance = None
__app = None

__this = sys.modules[__name__]
__this.instance_counter = 0
__this.get_worker = lambda: __instance


CFG_KEY = 'IRRIGATION_CFG'


def init_app(app=None):
    global __app
    __app = app


def get_state():
    svc = None
    with suppress(AttributeError):
        svc = __instance
    if svc is None or (svc.stop_event.is_set() and svc.closed):
        return 'off'
    elif not svc.closed and svc.stop_event.is_set():
        return 'changig state currently, try again later'
    else:
        return 'on'
    return resp


def _load_config():
    with __app.app_context():
        config_file = current_app.config[CFG_KEY]
        cfg = irrigation.load_configuration(config_file)
        current_app.config.irrigation = cfg


def save_config(json_content):
    with __app.app_context():
        config_file = current_app.config[CFG_KEY]
        irrigation.store_configuration(config_file, json_content)


def get_config():
    with __app.app_context():
        return {
            'filename': os.path.basename(current_app.config[CFG_KEY]),
            'content': current_app.config.irrigation
            }


def start():
    _load_config()
    with __app.app_context():
        global __instance
        try:
            __instance = irrigation.run_and_return_by_conf_obj(
                current_app.config.irrigation)
        except:
            logging.exception(
                'Encountered exception during Gardener initialization:\n')
            stop()
            raise
        else:
            __this.instance_counter += 1


def stop():
    if __instance:
        __instance.__del__()
