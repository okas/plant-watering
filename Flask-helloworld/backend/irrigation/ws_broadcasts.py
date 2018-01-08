import logging
import blinker
from .. _globals import io
from .. import _utils
from . import signals
from . import service


log = logging.getLogger(__name__)
ns = '/irrigation'
room_pw = 'plantwatcher'


def make_plant_vm(plant):
    return {
        'name': plant.name,
        'state': plant.state.name,
        'moist_level': plant.moist_level,
        'moist_measured': plant.moist
        }


@signals.state_changed.connect_via(blinker.ANY)
def broadcast_service_status(sender, **kw):
    io.emit('service_status', sender, namespace=ns)


@signals.lib_water_level_changed.connect_via(blinker.ANY)
def broadcast_water_supply_state(sender, **kw):
    data = { 'waterLevel': sender.name }
    io.emit('water_supply_state', data, namespace=ns)


@signals.lib_water_consumed_changed.connect_via(blinker.ANY)
def broadcast_water_supply_state(sender, **kw):
    data = { 'waterConsum': sender }
    io.emit('water_consumed_changed', data, namespace=ns)


@_utils.suppress_on_empty_room(ns, room_pw)
def broadcast_update_plant_status(sender, **kw):
    plant = make_plant_vm(sender)
    io.emit('update_plant_status', plant, namespace=ns, room=room_pw)


def connect_plantwatcher():
    signals.lib_plant_status_changed.connect(broadcast_update_plant_status)


def disconnect_plantwatcher():
    signals.lib_plant_status_changed.disconnect(broadcast_update_plant_status)
