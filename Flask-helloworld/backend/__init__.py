import os
import sys
import logging
import importlib
import flask
import flask_cors
from . _globals import io
from . import http_routes
from . irrigation import service as irrigation_service # for pckg API


log = logging.getLogger(__name__)


def init(app):
    __setup_extensions(app)
    __setup_services(app)
    __setup_blueprints(app)


def __setup_extensions(app):
    flask_cors.CORS(app)
    io.init_app(
        app,
        json=flask.json,
        async_mode='gevent',
        logger=logging.getLogger('flask_socketio'), # Refered in logging config!
        **app.config.get_namespace('SOCKETIO_')
        )


def __setup_services(app):
    irrigation_service.init(app)


def __setup_blueprints(app):
    app.register_blueprint(http_routes.bp)
