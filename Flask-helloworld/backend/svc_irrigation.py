import os
import sys
import logging
from contextlib import suppress
from flask import current_app

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


def start_new():
    with __app.app_context():
        current_app.config.irrigation = irrigation.load_configuration(
            current_app.config['IRRIGATION_CFG']
            )
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
    __instance.__del__()
