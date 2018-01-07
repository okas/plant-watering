import logging
import blinker
from .. _globals import io
from . import signals
from . import service


ns = '/irrigation'
log = logging.getLogger(__name__)


def _make_viewmodel(plant):
    return {
        'name': plant.name,
        'state': plant.state.name,
        'moist_level': plant.moist_level,
        'moist_measured': plant.moist
        }


@signals.state_changed.connect_via(blinker.ANY)
def broadcast_service_status(sender, **kw):
    io.emit('service_status', sender, namespace=ns)


@signals.lib_waterlevel_changed.connect_via(blinker.ANY)
def broadcast_water_supply_state(sender, **kw):
    data = { 'waterLevel': sender.name }
    io.emit('water_supply_state', data, namespace=ns)


@signals.lib_water_consumed_changed.connect_via(blinker.ANY)
def broadcast_water_supply_state(sender, **kw):
    data = { 'waterConsum': sender }
    io.emit('water_consumed_changed', data, namespace=ns)


@signals.lib_plant_status_changed.connect_via(blinker.ANY)
def broadcast_update_plant_status(sender, **kw):
    plant = _make_viewmodel(sender)
    io.emit('update_plant_status', plant, namespace=ns)
