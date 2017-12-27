import os
import sys
import json
import signal
import logging
import logging.config
from contextlib import suppress
import flask
import backend


log = logging.getLogger(__name__)


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
            backend.service_irrigation.stop()
        sys.exit(4)
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)


########################################################################

BASE_DIR = sys.path[0]
APP_NAME = os.path.basename(sys.path[0])
STATIC_FOLDER ='dist/static'
TEMPLATE_FOLDER ='dist'
ENVIRONMENT = os.getenv('PLANTWATER_ENVIRONMENT', 'production')

########################################################################

'''Application Factory'''
app = flask.Flask(
        import_name = APP_NAME,
        static_folder = STATIC_FOLDER,
        template_folder = TEMPLATE_FOLDER,
        instance_path = BASE_DIR+'/instance',
        instance_relative_config = True,
        root_path = BASE_DIR
        )
setup_flask_app_config(app, ENVIRONMENT)
setup_logging(app)
backend.init(app)
setup_cleanup()

# TODO: Where and what cleanup activities must be performed?

########################################################################

if app.config['IRRIGATION_SERVICE_AUTOSTART'] == True:
    try:
        backend.service_irrigation.start()
    except BaseException as err:
        log.exception(
            'Problem during application Irrigation service autostart!')
else:
    backend.service_irrigation._load_config()

