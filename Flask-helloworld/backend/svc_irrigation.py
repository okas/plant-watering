import os
import sys
import logging
from threading import Thread
from contextlib import suppress

sys.path.insert(1, os.path.dirname(sys.path[0]))
import irrigation


log = logging.getLogger(__name__)
instance_counter = 0


def start_new(app):
    global instance_counter
    app.config.irrigation = irrigation.load_configuration(
        app.config['IRRIGATION_CFG']
        )
    thread = Thread(name='Irrigation', target=__worker, args=(app,))
    instance_counter += 1
    thread.start()
    return thread


def __worker(app):
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
