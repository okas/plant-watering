import os
import sys
import argparse
sys.path.insert(1, os.path.abspath(__file__+'/../../'))

from irrigation._version import __version__


def get_config_choises():
    config_dir = os.path.abspath(__file__+'/../configuration/')
    configs = [x[:-5] for x in os.listdir(config_dir) if x.endswith('.json')]
    if len(configs) == 0:
        raise Exception(
            'Expected some *.json files in ../configuration/ !\n'\
            'Please add file using example file "default.json.example".'
            )
    for e in ('default', 'production', 'prod', '/'):
        if e != '/':
            try:
                default_index = configs.index(e)
            except:
                continue
        else:
            default_index = 0
        if default_index > -1:
            break
    return (configs, default_index)


def get_argument_data(config_choices, default_choise_index):
    parser = argparse.ArgumentParser(
        description='Lets water our plants! Version: '+__version__
        )
    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        required=False,
        help="Debug mode. Currently only for status logging behavior setting. "\
             "This flag takes precedence over configuration setting."
        )
    parser.add_argument(
        '-c', '--config',
        choices=config_choices,
        default=config_choices[default_choise_index],
        required=False,
        help="Default is [%(default)s]. Program configuration."\
             "There is selection of *.json file names, that where "\
             "found from ../configuration/. "\
             "You must fill in configurations before program can run!"
        )
    return parser.parse_args()


def setup_logging(is_debug):
    import logging
    logging.basicConfig(
        style='{',
        format='{asctime} | {threadName} | {message}',
        level=logging.DEBUG if is_debug else logging.INFO
        )


def run_app(config):
    from irrigation import Gardener
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


if __name__ == '__main__':
    choises_data = get_config_choises()
    parsed_arguments = get_argument_data(*choises_data)
    from irrigation.configuration import load_configuration
    cfg = load_configuration(parsed_arguments.config)
    setup_logging(cfg.debug or parsed_arguments.debug)
    run_app(cfg)
