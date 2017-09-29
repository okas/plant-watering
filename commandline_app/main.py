import sys
import config
from core import Gardener
from common import common_logger as log


def main(config_name_or_path):
    gardener = None
    app_configuration = config.load_configuration(config_name_or_path)
    _err = None
    try:
        gardener = Gardener(app_configuration)
        gardener.stop_event.wait()
    except (KeyboardInterrupt):
        log("! Received keyboard interrupt.\n")
    except SystemExit as err:
        log("Someting wants to SystemExit...\n")
        _err = err
    except Exception as err:
        log("Encountered some exeption, should see it after "\
            "'Program done' message below.")
        _err = err
    finally:
        if gardener is not None:
            gardener.stop_event.set()
            gardener.close()
    log("Program done.\n")
    if _err is not None:
        log("Re-raised error, that occured during program execution:\n")
        raise _err
    sys.exit()


if __name__ == '__main__':
    # it is used only if this file is started explicitly.
    main('test1')
