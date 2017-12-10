import os
#from flask_debugtoolbar import DebugToolbarExtension
#toolbar = DebugToolbarExtension(app)

# Refer to default.py file for all custom configurations

DEBUG = True

#WERKZEUG_DEBUG_PIN = 'off'

CORS_ORIGINS = r'.*http://saarmas-rp3-1.saared.eu.*'

IRRIGATION_SERVICE_AUTOSTART = True

del os
