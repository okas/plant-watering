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


def load_config():
    with __app.app_context():
        config_file = current_app.config['IRRIGATION_CFG']
        cfg = irrigation.load_configuration(config_file)
        current_app.config.irrigation = cfg


def save_config(json_content):
    with __app.app_context():
        config_file = current_app.config['IRRIGATION_CFG']
        with open(config_file, 'w', encoding='utf8') as outfile:
            json.dump(json_content, outfile, ensure_ascii=False, indent=4)


def start_new():
    load_config()
    with __app.app_context():
        global __instance
        try:
            __instance = irrigation.run_and_return_by_conf_obj(
                current_app.config.irrigation
                )
        except BaseException as err:
            logging.exception(
                'Encountered exception during Gardener initialization:\n')
        __this.instance_counter += 1


def stop():
    if __instance:
        __instance.__del__()
