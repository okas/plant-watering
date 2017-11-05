from version import __version__

import os
import argparse


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
        description='Lets water our plants!'
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
        "There is selection of *.json file names, that where found "\
        "from ../configuration/. "\
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


def main():
    choises_data = get_config_choises()
    parsed_arguments = get_argument_data(*choises_data)
    import configuration
    cfg = configuration.load_configuration(parsed_arguments.config)
    setup_logging(cfg.debug or parsed_arguments.debug)
    import __init__
    __init__.run_commandline(cfg)


if __name__ == '__main__':
    main()

del os
del argparse

