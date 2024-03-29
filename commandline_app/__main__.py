import os
import sys
import signal
import argparse
from contextlib import suppress
import logging
sys.path.insert(1, os.path.realpath(__file__+'/../../'))
import irrigation

from irrigation._version import __version__


def get_config_choises() -> tuple:
    cd = os.path.realpath(__file__+'/../configuration/')
    configs = {x[:-5]: cd+'/'+x for x in os.listdir(cd) if x.endswith('.json')}
    if len(configs) == 0:
        raise Exception(
            'Expected some *.json files in ../configuration/ !\n'\
            'Please add file using example file "default.json.example".'
            )
    for e in ('default', 'production', 'prod'):
        if e in configs:
            default_key = e
            break
    if default_key is None:
        default_key = [configs.keys()][0]
    return (configs, default_key)


def get_argument_data(config_choices, default_choise):
    parser = argparse.ArgumentParser(
        description="Let's water our plants! Version: "+__version__
        )
    parser.add_argument(
        '-l', '--log',
        choices=['info', 'debug'],
        nargs='+',
        required=False,
        help="If set, turns on logging. "\
             "It configures logging (Python std.lib.) module's logger."
        )
    parser.add_argument(
        '-c', '--config',
        choices=config_choices,
        default=default_choise,
        required=False,
        help="Default is [%(default)s]. Program configuration."\
             "There is selection of *.json file names, that where "\
             "found from ../configuration/. "\
             "You must fill in configurations before program can run!"
        )
    return parser.parse_args()


def setup_logging(level):
    if level:
        logging.basicConfig(
            style = irrigation.LOGGER_CONFIG['style'],
            format = irrigation.LOGGER_CONFIG['format'],
            level = logging._nameToLevel[level[0].upper()]
        )


def run_app(config_file):
    gardener = None
    exit_code = 0

    def handler(*_):
        with suppress(AttributeError):
            gardener.__del__()
        logger.info('Program got SIGTERM, but Gardener was closed gracefully.')
        sys.exit(4)

    signal.signal(signal.SIGTERM, handler)
    try:
        gardener = irrigation.run_and_return_by_conf_path(config_file)
        gardener.stop_event.wait()
    except KeyboardInterrupt:
        logging.debug("~ ~ ~ Received keyboard interrupt.\n")
        exit_code = 1
    except SystemExit as err:
        logging.exception("Someting wants to SystemExit.\n")
        exit_code = 2
    except BaseException as err:
        logging.exception("Encountered exception, "\
                          "probably during Gardener initialization:\n")
        exit_code = 3
    finally:
        if gardener is not None:
            gardener.__del__()
    logging.info("Program done.\n")
    return exit_code


if __name__ == '__main__':
    config_files, default_coise = get_config_choises()
    parsed_arguments = get_argument_data(
        config_files.keys(),
        default_coise
        )
    setup_logging(parsed_arguments.log)
    asked_config_file = config_files[parsed_arguments.config]
    code = run_app(asked_config_file)
    sys.exit(code)
