import os
#from flask_debugtoolbar import DebugToolbarExtension
#toolbar = DebugToolbarExtension(app)

# Refer to default.py file for all custom configurations

DEBUG = True

#WERKZEUG_DEBUG_PIN = 'off'

CORS_ORIGINS = r'.*//saarmas-rp3-1.saared.eu.*'

SOCKETIO_ENGINEIO_LOGGER = False

""" Closing a program with Ctrl-C causes some error, if autostart is disabled """
IRRIGATION_SERVICE_AUTOSTART = True

del os
