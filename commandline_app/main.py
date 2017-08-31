import sys
import atexit
import signal
import config
from time import sleep
from threading import main_thread
from core import Gardener
from common import common_logger as log


def main(mode):
    if mode == 'prod':
        config_callback = config.load_cfg_prod
    elif mode == 'test1':
        config_callback = config.load_cfg_test1
    else:
        raise Exception("mode '%s' is not implemented in main.main()!")
    __run_program(config_callback)

def __run_program(config_callback):
    # TODO: pass GPIO or some other initialization data from some module/mixin?
    __gardener = None

    def __signal_handler(*args):
        print("here")
        __gardener.close()
        sleep(10)
        log("Exit %s (from cleanup handler).\n" % main_thread().name)

    #atexit.register(__cleanup_handler, __gardener, __watertank, Plant.shared_pump)
    signal.signal(signal.SIGTERM, __signal_handler)
    #signal.signal(signal.SIGKILL, __signal_handler)
    _err = None
    try:
        # set up Gardener object graph
        gardener_args, tank_args, plants_args = config_callback()
        __gardener = Gardener(tank_args, plants_args, **gardener_args)
        # start garden monitoring
        __gardener.start_work()
        __gardener.stop_event.wait()
    except (KeyboardInterrupt):
        log("! Received keyboard interrupt.\n")
    except SystemExit as err:
        log("Someting wants to SystemExit...\n")
        _err = err
    except Exception as err:
        log("Encountered some exeption, should see it after 'Program done' message below.")
        _err = err
    finally:
        if __gardener is not None: __gardener.stop_and_close()
    log("Program done.\n")
    if _err is not None:
        log("Re-raised error, that occured during program execution:\n")
        raise _err
    sys.exit()

def _plant_manipulator_worker(index, wait_for, stop_event, cycles=0):
    # obsolete: use this instead: gpiozero.tools module, artificial sources
    counter = 1
    value_to_set = 20
    while counter <= cycles or cycles == 0:
        if stop_event.is_set(): return
        plant = Gardener.plants[index]
        while plant.state != State.resting: sleep(0.1)
        log("manipulated %s\'s sensor to %d. (times: %d/%d)."\
                      % (plant.id, value_to_set, counter, cycles))
        plant.sensor.value = value_to_set
        sleep(wait_for)
        counter += 1

def __cleanup_handler(*args):
    print("here")
    print(args)
    for target in args:
        print("target not none?: %s" % (target is not None))
        if target is not None: target.close()
    sleep(5)
    log("Exit %s (from cleanup handler).\n" % main_thread().name)


if __name__ == '__main__':
    # it is used only if this file is started explicitly.
    main('test1')
