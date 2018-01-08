import os
import sys
import json
import signal
import logging
import logging.config
import flask
import eventlet
eventlet.monkey_patch()

# To ensure that app's dependencies outside the package can be imported.
# TODO: find a way to move it outside, some "requirements.txt" file.
sys.path.insert(1, os.path.dirname(sys.path[0]))
import backend

log = logging.getLogger(__name__)


def setup_flask_app_config(app, environment):
    app.config.from_pyfile('secrets.py')
    app.config.from_object('config.default')
    app.config.from_object('config.{}'.format(environment))


def setup_logging(app):
    with open(app.config['IRRIGATION_LOGGING']) as j_file:
        logging.config.dictConfig(json.load(j_file))


def setup_cleanup():
    def handler(*_):
        backend.irrigation_service.stop()
        # TODO: should add socketio closing ?
        eventlet.StopServe
        sys.exit(4)
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)


########################################################################

BASE_DIR = sys.path[0]
APP_NAME = os.path.basename(sys.path[0])
STATIC_FOLDER ='dist/static'
TEMPLATE_FOLDER ='dist'
ENVIRONMENT = os.getenv('IRRIGATION_ENVIRONMENT', 'production')

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
        backend.irrigation_service.start()
    except BaseException as err:
        log.exception(
            'Problem during application Irrigation service autostart!')
else:
    backend.irrigation_service.load_config()

backend.io.run(
    app,
    host=app.config['HOST'],
    port=app.config['PORT'],
    debug=app.config['DEBUG'],
    use_reloader=app.config['USE_RELOADER'],
    log_output=app.config['LOG_OUTPUT']
    )
