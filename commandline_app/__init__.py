from version import __version__

import os
import sys
sys.path.insert(1, os.path.abspath(__file__+'/../'))


def run_and_return(config_name_or_path):
    import configuration
    from core import Gardener
    cfg = configuration.load_configuration(config_name_or_path)
    return Gardener(cfg)


def run_commandline(config_name_or_path):
    from logging import debug
    gardener = None
    _err = None
    try:
        gardener = run_and_return(config_name_or_path)
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
    debug("Program done.\n")
    if _err is not None:
        debug("Re-raised error, that occured during program execution:\n")
        raise _err

del os
del sys
