import os
import sys
import json
import signal
import logging
import logging.config
from contextlib import suppress
from flask import Flask, current_app
from backend import setup_flask_and_blueprint, svc_irrigation


log = logging.getLogger(__name__)


def create_app(app_name, environment, static_folder, template_folder):
    '''Application Factory'''
    app = Flask(
        import_name = app_name,
        static_folder = static_folder,
        template_folder = template_folder,
        instance_path = BASE_DIR+'/instance',
        instance_relative_config = True
        )
    setup_flask_app_config(app, environment)
    setup_logging(app)
    setup_flask_and_blueprint(app)
    setup_cleanup()
    return app


def setup_flask_app_config(app, environment):
    app.config.from_pyfile('secrets.py')
    app.config.from_object('config.default')
    app.config.from_object('config.{}'.format(environment))


def setup_logging(app):
    with open(app.config['PLANTWATER_LOGGING']) as j_file:
        logging.config.dictConfig(json.load(j_file))


def setup_cleanup():
    def handler(*_):
        with suppress(AttributeError):
            svc_irrigation.stop()
        sys.exit(4)
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)


########################################################################

BASE_DIR = sys.path[0]
APP_NAME = os.path.basename(sys.path[0])
STATIC_FOLDER ='./dist/static'
TEMPLATE_FOLDER ='./dist'
ENVIRONMENT = os.getenv('PLANTWATER_ENVIRONMENT', 'production')

########################################################################

app = create_app(APP_NAME, ENVIRONMENT, STATIC_FOLDER, TEMPLATE_FOLDER)

########################################################################

if app.config['IRRIGATION_SERVICE_AUTOSTART'] == True:
    svc_irrigation.start_new()
########################################################################
