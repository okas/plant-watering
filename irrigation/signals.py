from blinker import Namespace


irrigation_signals = Namespace(name=__package__)

water_level_changed = irrigation_signals.signal('water_level_changed')
water_consumed_changed = irrigation_signals.signal('water_consumed_changed')
plant_status_changed = irrigation_signals.signal('plant_status_changed')


del Namespace
