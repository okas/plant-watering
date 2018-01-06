import os
#from flask_debugtoolbar import DebugToolbarExtension
#toolbar = DebugToolbarExtension(app)

# Refer to default.py file for all custom configurations
HOST='::'
PORT=4999
DEBUG = False
USE_RELOADER = False

#WERKZEUG_DEBUG_PIN = 'off'

CORS_ORIGINS = r'.*//saarmas-rp3-1.saared.eu.*'

# TODO: test!
SOCKETIO_CORS_ALLOWED_ORIGINS = [
    'http://saarmas-rp3-1.saared.eu:8080'
]

SOCKETIO_ENGINEIO_LOGGER = False

SOCKETIO_ALLOW_UPGRADES = True

"""
Closing a program with Ctrl-C causes some error, if autostart is disabled.
Update: if service is not running, when Ctrl-C i spressed, then there will be error.
"""
IRRIGATION_SERVICE_AUTOSTART = True

del os
