"""Dette modul kører simuleringen af kølerummet for en måned.

    Returns:
        _type_: dict - Samlet data for simuleringen af kølerummet for en måned
"""
import math
import random

from termostat import Thermostat


class Kølerum:
    def __init__(self, thermostat: Thermostat, energy_prices):

        self.t_rum = 20  # Rumtemperatur
        self.t_komp = -5  # Kompressorens køletemperatur
        self.delta_t = 300  # 5 minutter
        self.t_start = 5  # Starttemperatur
        self.t_target = 5  # Mål for temperatur

        self.t_current = self.t_start  # Starter på 5 grader men ændres
        self.door_open = False  # Døren er lukket til at starte med
        self.compressor_on = False  # Kompressoren er slukket til at starte med

        self.n = 0  # 0 minutter er gået
        self.food_waste = [0 for i in range(8640)]  # Madspild
        self.temps = [0 for i in range(8640)]  # Temperatur
        self.electricity_cost = [0 for i in range(8640)]  # Elpris  # Samlet pris

        self.energy_prices = energy_prices
        self.termostat = thermostat

    def decide_constants(self, door: bool, compressor: bool) -> float:
        """Bestemmer hvilke konstanter der skal bruges til at beregne temperaturen

        Args:
            door (bool): True if open
            compressor (bool): True if on

        Returns:
            float: the constants

        Examples:
            >>> k = Kølerum(thermostat=None, energy_prices=[])
            >>> k.decide_constants(True, True)
            (3.0000000000000004e-05, 8e-06)
        """
        if door:  # Døren er åben
            c_1 = 3 * (10**-5)
        else:  # Døren er lukket
            c_1 = 5 * (10**-7)
        if compressor:  # Kompr tændt
            c_2 = 8 * (10**-6)
        else:  # Kompr slukket
            c_2 = 0
        return c_1, c_2

    def decide_door(self, percentage=0.1) -> bool:
        """Bestemmer om døren skal være åben eller lukket

        Args:
            percentage (float, optional): Procent chance for at døren er åben (10%). Defaults to 0.1.
            Yes
        Returns:
            _type_: bool - True if open
        Examples:
            >>> k = Kølerum(thermostat=None, energy_prices=[])
            >>> random.seed(0)
            >>> k.decide_door(1.0)
            True
            >>> k.decide_door(0.0)
            False
        """
        return random.random() <= percentage

    def get_new_temperature(self) -> float:
        """Beregner den nye temperatur og inkrementerer n med steps på 5 minutter

        Returns:
            _type_: new temperature
        """
        self.temps[self.n] = self.t_current  # Tilføjer temperaturen til en liste
        self.door_open = self.decide_door()  # Bestemmer om døren er åben
        self.compressor_on = self.termostat.update_compressor(
            self.t_current, self.n
        )  # Bestemmer om kompressoren er tændt
        c_1, c_2 = self.decide_constants(
            self.door_open, self.compressor_on
        )  # Bestemmer konstanterne

        delta_t_current_rum = self.t_rum - self.t_current
        delta_t_current_komp = self.t_komp - self.t_current
        new_temp = (
            self.t_current
            + (c_1 * delta_t_current_rum + c_2 * delta_t_current_komp) * self.delta_t
        )  # Beregner den nye temperatur
        self.t_current = new_temp  # Opdaterer temperaturen
        self.n += 1  # Inkrementerer n
        return new_temp

    def calculate_food_waste(self) -> None:
        """Beregner madspildet og tilføjer det til en liste for en total pr. måned"""
        if self.t_current < 3.5:
            self.food_waste[self.n] = 4.39 * math.exp(-0.49 * self.t_current)
              # Frostskade
        elif self.t_current > 6.5:
            self.food_waste[self.n] = 0.11 * math.exp(0.31 * self.t_current)
              # Bakterievækst
        else:
            pass
    def calculate_electricity_price(self) -> None:
        """Bereneger elprisen og tilføjer det til en liste for en total pr. måned"""
        if self.compressor_on:
            self.electricity_cost[self.n] = float(self.energy_prices[self.n]["Pris"]) 
        else:
            pass  # Hvis kompressoren er slukket

    def sum_up_cost(self) -> dict:
        """Sumerer alt dataen og returnerer det

        Returns:
            dict: a collection of the data
        """
        return {
            "temperature_log": self.temps,
            "electricity_log": self.electricity_cost,
            "food_waste_log": self.food_waste,
            "total_cost": sum(self.electricity_cost) + sum(self.food_waste),
        }

    def step(self):
        """Kører simulationen for 5 minutter"""
        self.calculate_food_waste()
        self.calculate_electricity_price()
        self.get_new_temperature()

    def run_simulation(self):
        """Kører simulationen for en måned"""
        for _ in range(8640):
            self.step()
        return self.sum_up_cost()


if __name__ == "__main__":
    """Dette er blot for at det er muligt at se hvad hvert enkelt modul gør og køre doctest"""
    import csv
    import doctest

    from termostat import ThermostatSemiSmart, ThermostatSimple

    with open("elpris.csv") as elpris:
        energy_prices = list(csv.DictReader(elpris))

    # Create an instance of ThermostatSemiSmart
    thermostat = ThermostatSemiSmart(energy_prices)

    # Create an instance of Kølerum with the thermostat instance
    KØL = Kølerum(thermostat=thermostat, energy_prices=energy_prices)
    print(doctest.testmod())
