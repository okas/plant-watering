from flask import Flask
from website import setup_website


def create_app():
	'''Application Factory'''
	app = Flask('website', instance_relative_config=True)
	__load_configurations(app)
	setup_website(app)
	return app


def __load_configurations(app):
	# Load the default configuration
	app.config.from_object('config.default')

	# Load the application secrets that cannot be in version control
	app.config.from_pyfile('secrets.py')

	# Load the config to select desired application configuration.
	# Similar to environment variable level selection: staging, dev, prod
	try: app.config.from_pyfile('set_config.py')
	except IOError: pass
	else:
		config_name = app.config['MYAPP_CONFIG_NAME']

	try:
		app.config.from_object('config.%s' % config_name)
	except IOError: pass

	#app.config.from_pyfile('set_config.py')

	# Load the file specified by the APP_CONFIG_FILE environment variable
	# Variables defined here will override those in the default configuration
	try: app.config.from_envvar('MYAPP_CONFIG_FILE')
	except: pass

	# Some check to ensure that if spec config is not loaded, then notify and exit


if __name__ == '__main__':
	app = create_app()
	app.run(host='0.0.0.0') # port=81 ? # debug values is set at config.py
