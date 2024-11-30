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
        self.t_target_low = 3  # Lower boundary
        self.t_target_high = 6.2  # Upper boundary
        self.energy_prices = energy_prices

    def update_compressor(self, t_current, n):
        current_price = float(self.energy_prices[n]["Pris"])
        threshold_price = 2

        if t_current >= self.t_target_high:
            return True
        elif current_price <= threshold_price and n < 3000:
            return True
        elif t_current <= self.t_target_low:
            return False
        return False
