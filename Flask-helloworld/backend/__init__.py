import os
import sys
import importlib
import logging
import logging.config
import json
import signal
from threading import Thread
from contextlib import suppress
from flask import Flask
from flask_cors import CORS
sys.path.insert(1, os.path.realpath(__file__+'/../../../'))
import irrigation


def create_app(environment):
    '''Application Factory'''
    app = Flask(
        __name__,
        static_folder='../dist/static',
        template_folder='../dist',
        instance_relative_config=True
        )
    flask_app_config_loading(app, environment)
    setup_logging(app)
    CORS(app)
    register_blueprints(app)
    setup_plant_waterer(app)
    return app


def flask_app_config_loading(app, environment):
    app.config.from_object('config.website_default')
    app.config.from_pyfile('secrets.py')
    app.config.from_object('config.{}'.format(environment))
    app.config.from_envvar('PLANTWATER_OVERRIDES', silent=True)
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config.irrigation = irrigation.load_configuration(
        app.config['IRRIGATION_CFG']
        )


def setup_logging(app):
    with open(app.config['PLANTWATER_LOGGING']) as f:
        logging.config.dictConfig(json.load(f))


def register_blueprints(app):
    flask_views = ['.index', '.api']
    for module in flask_views:
        m = importlib.import_module(module, __name__)
        app.register_blueprint(m.bp)


def setup_plant_waterer(app):
    #from werkzeug.serving import is_running_from_reloader
    def handler(*_):
        with suppress(AttributeError):
            app.plant_waterer.__del__()
        sys.exit(4)

    def worker():
        exit_code = 0
        try:
            app.plant_waterer = irrigation.run_and_return_by_conf_obj(
                app.config.irrigation
                )
            app.plant_waterer.stop_event.wait()
        except BaseException as err:
            logging.exception("Encountered exception, "\
                              "probably during Gardener initialization:\n")
            exit_code = 2
        finally:
            with suppress(AttributeError):
                app.plant_waterer.__del__()
                logging.debug('Exiting from Garndener worker thread.')
            sys.exit(exit_code)
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    thread = Thread(name='Irrigation', target=worker)
    thread.start()
