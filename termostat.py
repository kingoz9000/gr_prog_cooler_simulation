import csv
from abc import ABC, abstractmethod


class Thermostat(ABC):
    pass

    @abstractmethod
    def update_compressor(self):
        pass

    def calculate_responsible_time_to_power_on(self):
        pass


class ThermostatSimple(Thermostat):
    def __init__(self):
        self.t_target = 5 

    def update_compressor(self, t_current, n):
        return t_current > self.t_target


class ThermostatSmart(Thermostat):
    def __init__(self, energy_prices=None):
        self.t_target = 6 
        self.n = 0
        if energy_prices is None:
            with open("elpris.csv") as elpris:
                self.energy_prices = list(csv.DictReader(elpris))
        else:
            self.energy_prices = energy_prices

    def update_compressor(self, t_current, n):
        future_prices = [float(row["Pris"]) for row in self.energy_prices[n : n + 5]]
        average_future_price = sum(future_prices) / len(future_prices)
        if t_current > self.t_target:
            if 4 < t_current > 6:
                return True
            elif average_future_price > float(self.energy_prices[self.n]["Pris"]):
                return True
            else:
                return False
