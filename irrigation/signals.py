from blinker import Namespace

irrigation_signals = Namespace(name='irrigation')
irrigation_signals.signal('water_level_changed')
