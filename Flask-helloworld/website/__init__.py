import os
import sys
import signal
from flask import Flask
from werkzeug.serving import is_running_from_reloader
sys.path.insert(1, os.path.abspath(__file__+'/../../../'))
import commandline_app


def create_app(environment):
    '''Application Factory'''
    app = Flask(__name__, instance_relative_config=True)
    configure_webapp(app, environment)
    setup_webapp(app)
    setup_plant_waterer(app)
    return app


def setup_webapp(web_app):
    from .views import test
    web_app.register_blueprint(test.mod)


def configure_webapp(web_app, environment):
    web_app.config.from_object('config.default')
    web_app.config.from_pyfile('secrets.py')
    web_app.config.from_object('config.{}'.format(environment))
    web_app.config.from_envvar('PLANTWATER_OVERRIDES', silent=True)
    web_app.jinja_env.auto_reload = True
    web_app.config['TEMPLATES_AUTO_RELOAD'] = True


def setup_plant_waterer(web_app):
    gardener = None
    try:
        gardener = commandline_app.run_and_return('test1')
    except Exception as err:
        print("Encountered some exception during starting of Gardener instance. "\
              "Details should follow...")
        if gardener is not None:
            gardener.__del__()
            print("Re-raised error, that occured during program execution:\n")
        raise err
    else:
        web_app.plant_waterer = gardener

    def handler(*a):
        if hasattr(web_app, 'plant_waterer'):
            web_app.plant_waterer.__del__()
            sys.exit()

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

