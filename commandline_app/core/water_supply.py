from threading import Event
from .plant import Plant, State
from hardware import Pump, WaterTank


class WaterSupply():
    def __init__(
            self,
            stop_event,
            pump_args,
            tank_args
            ):
        self.stop_event = stop_event
        self.available_event = Event()
        self.pump = Pump(pump_args)
        self.__tank_thread = WaterTank(
            self.stop_event,
            self.available_event,
            **tank_args
            )
        self.__tank_thread.start()

    def __cannot_pump(self):
        return self.stop_event.is_set() or not self.available_event.is_set()

    def watering(self, plant):
        if self.__cannot_pump():
            log("cannot start pump at this time!")
        else:
            old_state = plant.state
            plant.state = State.watering
            log("   started pumping water.")

            stats = self.pump.pump_millilitres(
                plant.pour_millilitres,
                plant.valve,
                plant.pump_power
                )

            self.pump.reached_event.set()

            stoppable_sleep(self.watering_time, self.__cannot_pump)


            log("  ... %.3f seconds" % stats.time_elaps)
            plant.state = State.remeasure if not override else old_state
            log("   done pumping water.")

    def stop_and_close(self):
        log("Ending WaterSupply, quitting worker thread. Please wait...\n")
        self.closed = False
        self.stop_event.set()
        self.__tank_thread.join()
        self.closed = True
        log("Completed Gardener!\n")

    def __del__(self):
        if hasattr(self, 'closed') and not self.closed:
            self.stop_and_close()
