import os
import sys
import json
import signal
import logging
import logging.config
from contextlib import suppress
from flask import Flask
#from backend import
from backend import setup_flask_and_blueprint, svc_irrigation
#import backend.svc_irrigation


def create_app(app_name, environment, static_folder, template_folder):
    '''Application Factory'''
    app = Flask(
        import_name=app_name,
        static_folder=static_folder,
        template_folder=template_folder,
        instance_relative_config=True
        )
    setup_flask_app_config(app, environment)
    setup_logging(app)
    setup_flask_and_blueprint(app)
    setup_cleanup(app)
    return app


def setup_flask_app_config(app, environment):
    app.config.from_pyfile('secrets.py')
    app.config.from_object('config.default')
    app.config.from_object('config.{}'.format(environment))
    app.config.from_envvar('PLANTWATER_OVERRIDES', silent=True)
    app.config.from_envvar('IRRIGATION_SVC_START', silent=True)


def setup_logging(app):
    with open(app.config['PLANTWATER_LOGGING']) as f:
        logging.config.dictConfig(json.load(f))


def setup_cleanup(app):
    def handler(*_):
        with suppress(AttributeError):
            app.plant_waterer.__del__()
        sys.exit(4)
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)


########################################################################
APP_NAME = os.path.basename(sys.path[0])
STATIC_FOLDER ='./dist/static'
TEMPLATE_FOLDER ='./dist'
########################################################################
app = create_app(
    APP_NAME,
    os.getenv('PLANTWATER_ENVIRONMENT', 'production'),
    STATIC_FOLDER,
    TEMPLATE_FOLDER
    )
if app.config['IRRIGATION_SVC_START'] == True:
    service_thread = svc_irrigation.start_new(app)

