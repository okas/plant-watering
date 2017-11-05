from version import __version__


from core import Gardener


def run_and_return(config_name_or_path):
    import configuration
    cfg = configuration.load_configuration(config_name_or_path)
    return Gardener(cfg)


def run_commandline(config):
    import sys
    import logging
    gardener = None
    exit_code = 0
    try:
        gardener = Gardener(config)
        gardener.stop_event.wait()
    except KeyboardInterrupt:
        logging.debug("~~~ Received keyboard interrupt.\n")
        exit_code = 1
    except SystemExit as err:
        logging.exception("Someting wants to SystemExit.\n")
        exit_code = 2
    except BaseException as err:
        logging.exception("Encountered exception, "\
                          "probably during Gardener initialization.\n")
        exit_code = 3
    finally:
        if gardener is not None:
            gardener.__del__()
    logging.info("Program done.\n")
    sys.exit(exit_code)
