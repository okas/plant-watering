import os
import sys


# Statement for enabling the development environment NB! Use separate development.py config file!
DEBUG = False

# Define the application directory
BASE_DIR = sys.path[0]

PLANTWATER_LOGGING = BASE_DIR + '/config/logging.json'

# Define the database - we are working with
# SQLite for this example
#SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
#DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 6

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True

CORS_ORIGINS = "<specify>"

WEBPACK_MANIFEST_PATH = BASE_DIR + '/website/build/webpack.manifest.json'

IRRIGATION_CFG = BASE_DIR + '/instance/irrigation_test1.json'

# If true, then service is started immediately. Otherwise it can be started later.
IRRIGATION_SERVICE_AUTOSTART = True

del os
del sys
