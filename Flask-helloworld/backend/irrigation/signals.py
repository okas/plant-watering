from blinker import Namespace
from irrigation import irrigation_signals


service_sigals = Namespace(name=__package__)

state_changed = service_sigals.signal('state_changed')


lib_water_level_changed = irrigation_signals.signal('water_level_changed')
lib_water_consumed_changed = irrigation_signals.signal('water_consumed_changed')
lib_plant_status_changed = irrigation_signals.signal('plant_status_changed')


del irrigation_signals
del Namespace
