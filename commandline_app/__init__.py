from version import __version__

import os
import sys
from core import Gardener


def run_and_return(config_name_or_path):
    import configuration
    cfg = configuration.load_configuration(config_name_or_path)
    return Gardener(cfg)


def run_commandline(config):
    from logging import debug, info
    gardener = None
    _err = None
    try:
        gardener = Gardener(config)
        gardener.stop_event.wait()
    except (KeyboardInterrupt):
        debug("! Received keyboard interrupt.\n")
    except SystemExit as err:
        debug("Someting wants to SystemExit...\n")
        _err = err
    except Exception as err:
        debug("Encountered some exeption, should see it after "\
            "'Program done' message below.\n")
        _err = err
    finally:
        if gardener is not None:
            gardener.__del__()
    info("Program done.\n")
    if _err is not None:
        debug("Re-raised error, that occured during program execution:\n")
        raise _err

del os
del sys

