"""Dette modul indeholder klasser til at styre termostater.

    Returns:
        bool: True hvis kompressoren skal tændes, ellers False.
"""
import csv
from abc import ABC, abstractmethod


class Thermostat(ABC):

    @abstractmethod
    def update_compressor(self):
        """
        Noget om funktionen
        """



class ThermostatSimple(Thermostat):
    def __init__(self, energy_prices=None):
        self.t_target = 5

    def update_compressor(self, t_current, n):
        return t_current > self.t_target


class ThermostatSemiSmart(Thermostat):
    def __init__(self, energy_prices=None):
        self.t_target = 6.4

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