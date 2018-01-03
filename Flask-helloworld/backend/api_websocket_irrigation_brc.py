import logging
import blinker
from . _globals import socketio, irrigation_signals
from . import service_irrigation

#TODO: See dependency handling possibilities near disconnect()
# See: https://github.com/miguelgrinberg/Flask-SocketIO/blob/master/flask_socketio/__init__.py

ns = '/irrigation'
log = logging.getLogger(__name__)
water_level_changed = irrigation_signals.signal('water_level_changed')
plant_status_changed = irrigation_signals.signal('plant_status_changed')


def _make_viewmodel(plant, force_measure=False):
    state = None
    moist = None
    if force_measure:
        state, moist = plant.state_full_measured[:2]
    return {
        'name': plant.name,
        'state': (state or plant.state).name,
        'moist_level': plant.moist_level,
        'moist_measured': moist or plant.moist
        }


@service_irrigation.state_changed.connect_via(blinker.ANY)
def broadcast_service_status(sender, **kw):
    socketio.emit('service_status', sender, namespace=ns)


@water_level_changed.connect_via(blinker.ANY)
def broadcast_water_supply_state(sender, **kw):
    data = { 'waterLevel': sender.name }
    socketio.emit('water_supply_state', data, namespace=ns)


@plant_status_changed.connect_via(blinker.ANY)
def broadcast_update_plant_status(sender, **kw):
    plant = _make_viewmodel(sender)
    socketio.emit('update_plant_status', plant, namespace=ns)
