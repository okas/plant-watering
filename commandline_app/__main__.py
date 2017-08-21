import argparse
import main


parser = argparse.ArgumentParser()
parser.add_argument('-m', '--mode',
                    choices=['prod', 'test1'],
                    default='prod',
                    help="Program mode. Default is 'prod', and it uses script's configs or config loader. "\
                    "Test profiles allow to apply predefined settings.")
main.main(parser.parse_args().mode)
