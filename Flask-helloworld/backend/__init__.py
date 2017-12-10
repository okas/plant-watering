import importlib
from flask_cors import CORS
from . import svc_irrigation


def setup_flask_and_blueprint(app):
    __setup_extensions(app)
    flask_controller_names = [
        '.index',
        '.api_plant'
        ]
    for module in flask_controller_names:
        m = importlib.import_module(module, __name__)
        app.register_blueprint(m.bp)


def __setup_extensions(app):
    CORS(app)
    svc_irrigation.init_app(app)
