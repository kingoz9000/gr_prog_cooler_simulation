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
        Bestemmer om kompressoren skal tændes.
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
        current_price = float(self.energy_prices[n]["Pris"])
        if current_price < 1:
            return True
        elif current_price < 2 and t_current > self.t_target:
            return True
        elif t_current > self.t_target and current_price < 3:
            return True
        elif t_current > self.t_target:
            return True
        
        

        