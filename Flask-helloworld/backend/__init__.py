import os
import sys
import logging
import importlib
import flask
import flask_cors
from . _globals import socketio
from . import (
    http_routes,
    apiws_default,
    apiws_irrigation,
    service_irrigation
    )


log = logging.getLogger(__name__)


def init(app):
    __setup_extensions(app)
    __setup_services(app)
    __setup_blueprints(app)


def __setup_extensions(app):
    flask_cors.CORS(app)
    socketio.init_app(
        app,
        json=flask.json,
        logger=log,
        **app.config.get_namespace('SOCKETIO_')
        )


def __setup_services(app):
    service_irrigation.init_app(app)


def __setup_blueprints(app):
    app.register_blueprint(http_routes.bp)
