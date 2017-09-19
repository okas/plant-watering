


class WaterSupply():
    def __init__(self, stop_event, pump_args, tank_args):
        self.stop_event = stop_event
        self.__pump = Pump()
        self.__tank_thread = WaterTank(
            self.stop_event,
            self.watering_event,
            self.tank_avail_evt,
            **tank_args
            )
        self.__tank_thread.start()
        ## consider to merge pump into water_tank as attribute and change name

        ## internaly there are events used
        ## consumer gets Condition and they will be notified
