import logging
import flask_socketio

socketio = flask_socketio.SocketIO()
logging.getLogger('flask_socketio').setLevel(logging.INFO)
