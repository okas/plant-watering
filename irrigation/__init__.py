from ._version import __version__

from .gardener import Gardener
from .configuration import load_configuration


def run_and_return(config_path):
    cfg = load_configuration(config_path)
    return Gardener(cfg)

__all__ = ['__version__', 'Gardener', 'load_configuration', 'run_and_return']
