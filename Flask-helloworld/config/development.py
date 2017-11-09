import os
#from flask_debugtoolbar import DebugToolbarExtension
#toolbar = DebugToolbarExtension(app)

# Statement for enabling the development environment
DEBUG = True

# Define the database - we are working with
# SQLite for this example
#SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
#DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
#THREADS_PER_PAGE = 2

IRRIGATION_CFG = '/home/pi/git-okas/plant-watering/Flask-helloworld/instance/irrigation_test1.json'

del os
