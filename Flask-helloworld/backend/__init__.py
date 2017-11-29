import os
import sys
import logging
import logging.config
import json
import signal
from threading import Thread
from contextlib import suppress
import jinja2
from flask import Flask
from flask.helpers import locked_cached_property
sys.path.insert(1, os.path.realpath(__file__+'/../../../'))
import irrigation
from . import (
    index
    )

def create_app(environment):
    '''Application Factory'''
    app = MyApp(
        __name__,
        static_folder='../dist/static',
        template_folders='../dist',
        instance_relative_config=True
        )
    flask_app_config_loading(app, environment)
    setup_logging(app)
    setup_webapp(app)
    setup_plant_waterer(app)
    return app


def flask_app_config_loading(app, environment):
    app.config.from_object('config.website_default')
    app.config.from_pyfile('secrets.py')
    app.config.from_object('config.{}'.format(environment))
    app.config.from_envvar('PLANTWATER_OVERRIDES', silent=True)
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config.irrigation = irrigation.load_configuration(
        app.config['IRRIGATION_CFG']
        )


def setup_logging(app):
    with open(app.config['PLANTWATER_LOGGING']) as f:
        logging.config.dictConfig(json.load(f))


def setup_webapp(app):
    app.register_blueprint(index.mod)


def setup_plant_waterer(app):
    #from werkzeug.serving import is_running_from_reloader
    def handler(*_):
        with suppress(AttributeError):
            app.plant_waterer.__del__()
        sys.exit(4)

    def worker():
        exit_code = 0
        try:
            app.plant_waterer = irrigation.run_and_return_by_conf_obj(
                app.config.irrigation
                )
            app.plant_waterer.stop_event.wait()
        except BaseException as err:
            logging.exception("Encountered exception, "\
                              "probably during Gardener initialization:\n")
            exit_code = 2
        finally:
            with suppress(AttributeError):
                app.plant_waterer.__del__()
                logging.debug('Exiting from Garndener worker thread.')
            sys.exit(exit_code)
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    thread = Thread(name='Irrigation', target=worker)
    thread.start()


class MyApp(Flask):
    '''
    credits: http://fewstreet.com/2015/01/16/flask-blueprint-templates.html
    '''
    def __init__(
            self,
            import_name,
            static_path=None,
            static_url_path=None,
            static_folder='static',
            template_folders=['templates'],
            instance_path=None,
            instance_relative_config=False,
            root_path=None):
        Flask.__init__(
            self,
            import_name,
            static_path,
            static_url_path,
            static_folder,
            template_folders,
            instance_path,
            instance_relative_config,
            root_path
            )

    @locked_cached_property
    def jinja_loader(self):
        file_loader = jinja2.FileSystemLoader(
            os.path.join(self.root_path, t) for t in self.template_folder
            )
        return jinja2.ChoiceLoader([
            file_loader,
            jinja2.PrefixLoader({}, delimiter = ".")
        ])

    def create_global_jinja_loader(self):
        return self.jinja_loader

    def register_blueprint(self, bp):
        Flask.register_blueprint(self, bp)
        self.jinja_loader.loaders[1].mapping[bp.name] = bp.jinja_loader
