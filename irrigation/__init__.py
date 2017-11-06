from ._version import __version__

#from .gardener import Gardener
#from .configuration import load_configuration
#from .water_tank import WaterTank
#from .plant import Plant, State
#from .water_supply import WaterSupply
#from .common import stoppable_sleep


#TODO only path should be accepted in future
def run_and_return(config_name_or_path):
    cfg = load_configuration(config_name_or_path)
    return Gardener(cfg)
