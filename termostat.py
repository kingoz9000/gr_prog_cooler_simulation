"""Dette modul indeholder klasser til at styre termostater der bliver brugt i kølerummet.

    Returns:
        bool: True hvis kompressoren skal tændes, ellers False.
"""

from abc import ABC, abstractmethod


class Thermostat(ABC):
    """Generel termostat der ikke kan noget for sig selv.

    Args:
        ABC: Abtract Base Class
    """
    @abstractmethod
    def update_compressor(self):
        """
        Bestemmer om kompressoren skal tændes.
        """


class ThermostatSimple(Thermostat):
    def __init__(self, energy_prices=None):
        """Initialiserer det simple termostat.

        Args:
            energy_prices (dict, optional): Ikke nødvendig her blot tilføjet for konsistens. Defaults to None.
        """
        self.t_target = 5

    def update_compressor(self, t_current, n):
        """Bestemmer om kompressoren skal tændes.

        Args:
            t_current (float): nuværende temperatur
            n (int): iteration

        Returns:
            bool: True hvis kompressoren skal tændes, ellers False.
        """
        return t_current > self.t_target


class ThermostatSemiSmart(Thermostat):
    def __init__(self, energy_prices=None):
        """Initialiserer det semi-smarte termostat.

        Args:
            energy_prices (dict, optional): Bruges ikke her. Defaults to None.
        """
        self.t_target = 6.4 # Måletemperatur

    def update_compressor(self, t_current, n):
        """Bestemmer om kompressoren skal tændes.

        Args:
            t_current (float): nuværende temperatur
            n (int): iteration

        Returns:
            bool: True hvis kompressoren skal tændes, ellers False.
        """
        return t_current > self.t_target


class ThermostatSmart(Thermostat):
    def __init__(self, energy_prices):
        """Initialiserer det smarte termostat.

        Args:
            energy_prices (dict): Priser på energi
        """
        self.t_target_low = 3  # Lavere grænse
        self.t_target_high = 6.2  # Øvre grænse
        self.energy_prices = energy_prices # Priser på energi

    def update_compressor(self, t_current, n):
        """Bestemmer om kompressoren skal tændes på baggrund af pris, temperatur og iteration.

        Args:
            t_current (float): nuværende temperatur
            n (int): iteration

        Returns:
            bool: True hvis kompressoren skal tændes, ellers False.
        """
        current_price = float(self.energy_prices[n]["Pris"])
        threshold_price = 2

        if t_current >= self.t_target_high:
            return True
        elif current_price <= threshold_price and n < 3000:
            return True
        elif t_current <= self.t_target_low:
            return False
        return False
