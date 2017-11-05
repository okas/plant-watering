from version import __version__

import os
import sys
from core import Gardener


def run_and_return(config_name_or_path):
    import configuration
    cfg = configuration.load_configuration(config_name_or_path)
    return Gardener(cfg)


def run_commandline(config):
    import logging
    gardener = None
    _err = None
    try:
        gardener = Gardener(config)
        gardener.stop_event.wait()
    except KeyboardInterrupt:
        logging.debug("! Received keyboard interrupt.\n")
    except SystemExit as err:
        logging.exception("Someting wants to SystemExit...\n")
        _err = err
    except BaseException as err:
        logging.exception("Encountered some exeption, should see it after "\
            "'Program done' message below.\n")
        _err = err
    finally:
        if gardener is not None:
            gardener.__del__()
    logging.info("Program done.\n")
    if _err is not None:
        logging.exception("Re-raised error, that occured during program execution:\n")
        raise _err

del os
del sys
