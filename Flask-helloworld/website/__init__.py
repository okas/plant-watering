import os
import sys
import logging
import signal
from threading import Thread
from contextlib import suppress
from flask import Flask
#from werkzeug.serving import is_running_from_reloader
sys.path.insert(1, os.path.realpath(__file__+'/../../../'))
import irrigation


def create_app(environment):
    '''Application Factory'''
    app = Flask(__name__, instance_relative_config=True)
    setup_logging(True)
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
    web_app.config.irrigation = irrigation.load_configuration(
        web_app.config['IRRIGATION_CFG']
        )


def setup_logging(is_debug):
    logging.basicConfig(
        style='{',
        format='{asctime} | {threadName} | {message}',
        level=logging.DEBUG if is_debug else logging.INFO
        )


def setup_plant_waterer(web_app):
    def handler(*_):
        with suppress(AttributeError):
            web_app.plant_waterer.__del__()
        sys.exit(4)

    def worker():
        exit_code = 0
        try:
            web_app.plant_waterer = irrigation.Gardener(
                web_app.config.irrigation
                )
            web_app.plant_waterer.stop_event.wait()
        except BaseException as err:
            logging.exception("Encountered exception, "\
                              "probably during Gardener initialization:\n")
            exit_code = 2
        finally:
            with suppress(AttributeError):
                web_app.plant_waterer.__del__()
                logging.debug('Exiting from Garndener worker thread.')
            sys.exit(exit_code)
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    thread = Thread(name='Gardener', target=worker)
    thread.start()
