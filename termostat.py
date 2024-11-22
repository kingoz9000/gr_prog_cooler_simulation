from abc import ABC, abstractmethod


class Thermostat(ABC):
    pass

    @abstractmethod
    def update_compressor(self):
        pass


class ThermostatSimple(Thermostat):
    def __init__(self, t_target):
        self.t_target = t_target

    def update_compressor(self, t_current):
        return t_current > self.t_target
