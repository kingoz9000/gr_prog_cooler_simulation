
import math
import random
import numpy as np
from termostat import Thermostat


class Kølerum:
    def __init__(self, thermostat: Thermostat, energy_prices, n: int = 8640):

        self.t_rum = 20 # Rumtemperatur
        self.t_komp = -5 # Kompressorens køletemperatur
        self.delta_t = 300 # 5 minutter
        self.t_start = 5 # Starttemperatur
        self.t_target = 5 # Mål for temperatur

        self.t_current = self.t_start # Starter på 5 grader men ændres
        self.door_open = False # Døren er lukket til at starte med
        self.compressor_on = False # Kompressoren er slukket til at starte med

        self.n = 0 # 0 minutter er gået
        self.food_waste = [] # Madspild
        self.temps = np.zeros(n) # Temperatur
        self.electricity_cost = [] # Elpris
        self.general_cost = [] # Samlet pris
        # Opens electricity prices
       
        self.energy_prices = energy_prices
        # Picks thermostat
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

    def precompute_door_states(self, n: int, percentage: float = 0.1):
        """
        Precompute door states for a given number of steps.

        Args:
            steps (int): Number of steps to simulate.
            percentage (float, optional): Probability of door being open. Defaults to 0.1.

        Returns:
            np.ndarray: An array of True/False values representing the door state.
    """
        return np.random.rand(n) <= percentage

    def get_new_temperature(self) -> float:
        """Beregner den nye temperatur og inkrementerer n med steps på 5 minutter

        Returns:
            _type_: new temperature
        """
        self.temps[self.n] = self.t_current # Tilføjer temperaturen til en liste
        self.door_open = self.precomputed_door_states[self.n] # Bestemmer om døren er åben
        self.compressor_on = self.termostat.update_compressor(self.t_current, self.n) # Bestemmer om kompressoren er tændt
        c_1, c_2 = self.decide_constants(self.door_open, self.compressor_on) # Bestemmer konstanterne

        delta_t_current_rum = self.t_rum - self.t_current
        delta_t_current_komp = self.t_komp - self.t_current
        combined_delta = (c_1 * delta_t_current_rum + c_2 * delta_t_current_komp)
        
        # Beregner den nye temperatur
        new_temp = self.t_current + combined_delta * self.delta_t
        
        self.t_current = new_temp # Opdaterer temperaturen
        self.n += 1 # Inkrementerer n
        return new_temp

    def calculate_food_waste(self) -> None:
        """Beregner madspildet og tilføjer det til en liste for en total pr. måned
        """
        t_current_array = np.array(self.temps)
        food_waste_array = np.zeros_like(t_current_array)

        frost_damage_mask = t_current_array < 3.5
        bacterial_growth_mask = t_current_array > 6.5

        food_waste_array[frost_damage_mask] = 4.39 * np.exp(-0.49 * t_current_array[frost_damage_mask])
        food_waste_array[bacterial_growth_mask] = 0.11 * np.exp(0.31 * t_current_array[bacterial_growth_mask])

        self.food_waste = food_waste_array.tolist()

    def calculate_electricity_price(self) -> None:
        """Bereneger elprisen og tilføjer det til en liste for en total pr. måned
        """
        n_steps = len(self.temps)
        electricity_cost_array = np.zeros(n_steps)

        # Ensure compressor_on_array is a boolean array
        compressor_on_array = np.array([self.termostat.update_compressor(temp, n) for n, temp in enumerate(self.temps)], dtype=bool)
        electricity_prices_array = np.array([float(self.energy_prices[n % len(self.energy_prices)]["Pris"]) for n in range(n_steps)])

        electricity_cost_array[compressor_on_array] = electricity_prices_array[compressor_on_array]

        self.electricity_cost = electricity_cost_array.tolist()

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
        """
        Kører simulationen for en måned.
        """
        self.temps = np.zeros(8640)
        self.precomputed_door_states = self.precompute_door_states(8640)

        for n in range(8640):
            self.get_new_temperature()

        self.calculate_food_waste()
        self.calculate_electricity_price()

        return self.sum_up_cost()



# Dette er blot for at det er muligt at se hvad hvert enkelt modul gør
if __name__ == "__main__":
    from termostat import ThermostatSemiSmart, ThermostatSimple
    import csv
    import doctest
    with open("elpris.csv") as elpris:
        energy_prices = list(csv.DictReader(elpris))

    
    # Create an instance of ThermostatSemiSmart
    thermostat = ThermostatSemiSmart(energy_prices)
    
    # Create an instance of Kølerum with the thermostat instance
    KØL = Kølerum(thermostat=thermostat, energy_prices=energy_prices)
    print(doctest.testmod())
    
