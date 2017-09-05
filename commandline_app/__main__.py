import argparse
import os
import main


config_dir = os.path.abspath(__file__+'/../config/')
configs = [x[:-5] for x in os.listdir(config_dir) if x.endswith('.json')]
if 'default' in configs:
    default_choice = 'default'
elif 'prod' in configs:
    default_choice = 'prod'
elif len(configs) > 0:
    default_choice = configs[0]
else:
    raise Exception(
        'Expected "default" or "prod" config existence in ../config/ !\n'\
        'Please add file using example file "default.json.example".\n'\
        'If valid file already exists then just rename one of them.'
        )
parser = argparse.ArgumentParser(
    description='Lets water our plants!'
    )
parser.add_argument(
    '-c', '--config',
    choices=configs,
    default=default_choice,
    required=False,
    help="Default is [%(default)s]. Program configuration."\
    "There is selection of *.json file names, that where found from ../config/. "\
    "You must fill in configurations before program can run!"
    )
main.main(parser.parse_args().config)
