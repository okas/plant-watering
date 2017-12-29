import os
import sys
import logging
import importlib
import flask
import flask_cors
from . _globals import socketio as __socketio
from . import (
    http_routes,
    websocket_default,
    websocket_irrigation,
    service_irrigation
    )


log = logging.getLogger(__name__)


def init(app):
    __setup_extensions(app)
    __setup_services(app)
    __setup_blueprints(app)
    __setup_websockets(app)


def __setup_extensions(app):
    flask_cors.CORS(app)
    __socketio.init_app(
        app,
        json=flask.json,
        logger=log,
        #TODO: Verify it!
        cors_allowed_origins=app.config['CORS_ORIGINS'],
        engineio_logger=True
        )


def __setup_services(app):
    service_irrigation.init_app(app)


def __setup_blueprints(app):
    app.register_blueprint(http_routes.bp)


def __setup_websockets(app):
    __socketio.on_namespace(websocket_default.DefaultNamespace())
    __socketio.on_namespace(websocket_irrigation.IrrigationNamespaceHandlers())
