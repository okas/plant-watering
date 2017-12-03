import importlib
from flask_cors import CORS


def setup_flask_and_blueprint(app):
    CORS(app)
    flask_controller_names = [
        '.index',
        '.api_plant'
        ]
    for module in flask_controller_names:
        m = importlib.import_module(module, __name__)
        app.register_blueprint(m.bp)
