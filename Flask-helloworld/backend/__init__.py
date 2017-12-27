import logging
import importlib
import flask
import flask_cors
import flask_socketio
from . import service_irrigation


log = logging.getLogger(__name__)
socketio = flask_socketio.SocketIO()
logging.getLogger('socketIO').setLevel(logging.INFO)


# update these lists as you add new routes or websockets.
# these modules will be imported with delay, which seems better for initialization.
http_and_api_modules = [
    '.http_routes',
    '.api_irrigation'
    ]
websocket_modules = [
    '.websocket_default',
    '.websocket_irrigation'
    ]


def init(app):
    __setup_extensions(app)
    __setup_blueprints(app)
    __setup_websockets(app)


def __setup_extensions(app):
    flask_cors.CORS(app)
    socketio.init_app(
        app,
        json=flask.json,
        logger=log,
        #TODO: Verify it!
        cors_allowed_origins=app.config['CORS_ORIGINS'],
        engineio_logger=True
        )
    service_irrigation.init_app(app)


def __setup_blueprints(app):
    for name in http_and_api_modules:
        module = importlib.import_module(name, __name__)
        blueprint = next(
            (var for var in dir(module).values()
                if isinstance(var, flask.Blueprint)),
            None
            )
        if blueprint:
            app.register_blueprint(blueprint)


def __setup_websockets(app):
    for name in websocket_modules:
        module = importlib.import_module(name, __name__)
        if callable(module.init):
            module.init(socketio)
        # for cls in
    socketio.on_namespace(websocket_irrigation.IrrigationNamespace())
