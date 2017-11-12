import os
import sys
import logging
import signal
from threading import Thread
from contextlib import suppress
from flask import Flask
from flask_webpack import Webpack
#from werkzeug.serving import is_running_from_reloader
sys.path.insert(1, os.path.realpath(__file__+'/../../../'))
import irrigation


def create_app(environment):
    '''Application Factory'''
    app = Flask(
        __name__,
        instance_relative_config=True
        )
    flask_app_config_loading(app, environment)
    flask_register_extensions(app)
    setup_logging(True)
    setup_webapp(app)
    setup_plant_waterer(app)
    return app


def setup_logging(is_debug):
    logging.basicConfig(
        style='{',
        format='{asctime} | {threadName} | {message}',
        level=logging.DEBUG if is_debug else logging.INFO
        )


def flask_app_config_loading(app, environment):
    app.config.from_object('config.default')
    app.config.from_pyfile('secrets.py')
    app.config.from_object('config.{}'.format(environment))
    app.config.from_envvar('PLANTWATER_OVERRIDES', silent=True)
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config.irrigation = irrigation.load_configuration(
        app.config['IRRIGATION_CFG']
        )


def flask_register_extensions(app):
    Webpack().init_app(app)


def setup_webapp(app):
    from .views import test
    app.register_blueprint(test.mod)


def setup_plant_waterer(app):
    def handler(*_):
        with suppress(AttributeError):
            app.plant_waterer.__del__()
        sys.exit(4)

    def worker():
        exit_code = 0
        try:
            app.plant_waterer = irrigation.Gardener(
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
    thread = Thread(name='Gardener', target=worker)
    thread.start()
