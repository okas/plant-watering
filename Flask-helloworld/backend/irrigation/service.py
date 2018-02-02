import os
import sys
import logging
from threading import BoundedSemaphore
from contextlib import suppress
from flask import current_app, json
from . import signals
import irrigation


log = logging.getLogger(__name__)
__stateChangeLock = BoundedSemaphore(1)

__this = sys.modules[__name__]
__this.instance_counter = 0
__this.get_worker = lambda: __instance

__instance = None
__app = None

CFG_KEY = 'IRRIGATION_CFG'


def init(app=None):
    global __app
    __app = app


def get_state(simple_state=False):
    svc = None
    with suppress(AttributeError):
        svc = __instance
    if svc is None or (svc.stop_event.is_set() and svc.closed):
        return {
            'state': 'off',
            'waterLevel': 'n/a',
            'waterConsum': 'n/a'
            } if not simple_state else { 'state': 'off' }
    elif not svc.closed and svc.stop_event.is_set():
        return {
            'state': 'unknown',
            'waterLevel': 'n/a',
            'waterConsum': 'n/a'
            } if not simple_state else { 'state': 'unknown' }
    else:
        return {
            'state': 'on',
            'waterLevel': svc.water_supply.water_level.name,
            'waterConsum': svc.water_consumed
            } if not simple_state else { 'state': 'on' }


def __load_config():
    with __app.app_context():
        config_file = current_app.config[CFG_KEY]
        cfg = irrigation.load_configuration(config_file)
        current_app.config.irrigation = cfg


def load_config():
    with __stateChangeLock:
        __load_config()


def save_config(json_content):
    with __stateChangeLock:
        with __app.app_context():
            config_file = current_app.config[CFG_KEY]
            irrigation.store_configuration(config_file, json_content)


def get_config():
    with __app.app_context():
        return {
            'filename': os.path.basename(current_app.config[CFG_KEY]),
            'content': current_app.config.irrigation
                if get_state(True)['state'] == 'on'
                else irrigation.load_configuration(current_app.config[CFG_KEY])
            }


def start():
    with __stateChangeLock:
        __load_config()
        with __app.app_context():
            global __instance
            try:
                __instance = irrigation.run_and_return_by_conf_obj(
                    current_app.config.irrigation)
            except:
                log.exception('%Encountered exception during Gardener '
                    'initialization:\n')
                __stop(True)
                raise
            else:
                __this.instance_counter += 1
                log.debug('%[{}] service is started'.format(__name__))
                signals.state_changed.send({
                    'state': 'on',
                    'waterLevel': __instance.water_supply.water_level.name,
                    'waterConsum': __instance.water_consumed
                    })


def __stop(on_cleanup=False):
        global __instance
        message = {
            'state': 'off',
            'waterLevel': 'n/a',
            'waterConsum': 'n/a'
            }
        if __instance:
            try:
                __instance.__del__()
            except:
                log.exception('%[{}] service didn\'t close cleanly!'.format(__name__))
                message['state'] = 'service-stopped-unclean-error'
                signals.state_changed.send(message)
            else:
                log.debug('%[{}] service is stopped'.format(__name__))
                if on_cleanup :
                    message['state'] = 'service-start-error'
                signals.state_changed.send(message)
            finally:
                __instance = None


def stop():
    with __stateChangeLock:
        __stop()
