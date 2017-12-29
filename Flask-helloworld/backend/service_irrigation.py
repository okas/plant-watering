import os
import sys
import logging
from contextlib import suppress
from flask import current_app, json
from blinker import Namespace
import irrigation


log = logging.getLogger(__name__)

#TODO: create global blinker signals/events catalog? names

__this = sys.modules[__name__]
__this.instance_counter = 0
__this.get_worker = lambda: __instance
__this.state = None

__instance = None
__app = None
__events = Namespace(name=__name__)

state_changed_event = __events.signal('state_changed_event')
CFG_KEY = 'IRRIGATION_CFG'


def init_app(app=None):
    global __app
    __app = app


def get_state():
    svc = None
    with suppress(AttributeError):
        svc = __instance
    if svc is None or (svc.stop_event.is_set() and svc.closed):
        return { 'state': 'off' }
    elif not svc.closed and svc.stop_event.is_set():
        return { 'state': 'changig state currently, try again later'}
    else:
        return { 'state': 'on' }
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
            logging.exception('Encountered exception during Gardener '
                'initialization:\n')
            stop(True)
            raise
        else:
            __this.instance_counter += 1
            if state_changed_event.receivers:
                state_changed_event.send('svc_start', state='on')


def stop(on_cleanup=False):
    if __instance:
        __instance.__del__()
        if state_changed_event.receivers:
            state_changed_event.send('svc_stop',
                state='service-start-error' if on_cleanup else 'off')
