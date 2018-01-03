import os
import sys
import logging
# from threading import Lock
from contextlib import suppress
from flask import current_app, json
from . _globals import service_irrigation_sigals
import irrigation


log = logging.getLogger(__name__)
state_changed = service_irrigation_sigals.signal('state_changed')
# TODO: add some lock for service state changing to handle race conditions.
# stateChangeLock = Lock()

__this = sys.modules[__name__]
__this.instance_counter = 0
__this.get_worker = lambda: __instance

__instance = None
__app = None

CFG_KEY = 'IRRIGATION_CFG'


def init_app(app=None):
    global __app
    __app = app


def get_state():
    svc = None
    with suppress(AttributeError):
        svc = __instance
    if svc is None or (svc.stop_event.is_set() and svc.closed):
        return {
            'state': 'off',
            'waterLevel': 'n/a',
            'waterConsum': 'n/a'
            }
    elif not svc.closed and svc.stop_event.is_set():
        return {
            'state': 'changig state currently, try again later',
            'waterLevel': 'n/a',
            'waterConsum': 'n/a'
            }
    else:
        return {
            'state': 'on',
            'waterLevel': svc.water_supply.water_level.name,
            'waterConsum': svc.water_consumed
            }


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
            logging.exception('Encountered exception during Gardener '
                'initialization:\n')
            stop(True)
            raise
        else:
            __this.instance_counter += 1
            state_changed.send({
                'state': 'on',
                'waterLevel': __instance.water_supply.water_level.name,
                'waterConsum': __instance.water_consumed
                })


def stop(on_cleanup=False):
    if __instance:
        __instance.__del__()
        state_changed.send({
            'state': 'service-start-error' if on_cleanup else 'off',
            'waterLevel': 'n/a',
            'waterConsum': 'n/a'
            })
        global __instance
        __instance = None
