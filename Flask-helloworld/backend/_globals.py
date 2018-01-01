import logging
import flask_socketio
from blinker import Namespace
from irrigation import irrigation_signals


socketio = flask_socketio.SocketIO()
logging.getLogger('flask_socketio').setLevel(logging.INFO)


service_irrigation_sigals = Namespace(name='backend.service_irrigation')
service_irrigation_sigals.signal('state_changed')
