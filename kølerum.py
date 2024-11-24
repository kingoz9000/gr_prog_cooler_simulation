import random
from termostat import ThermostatSimple, ThermostatSmart
import math
import csv


class Kølerum:
    def __init__(self, termostat="simple"):
        """Initializes the room cooler

        Args:
            termostat (str, optional): pick a thermostat. Defaults to "simple".
        """
        self.t_rum = 20
        self.t_komp = -5
        self.delta_t = 300
        self.t_start = 5
        self.t_target = 5
        
        self.t_current = self.t_start
        self.door_open = False
        self.compressor_on = False
        
        self.n = 0
        self.food_waste = []
        self.temps = []
        self.electicity_cost = []
        self.general_cost = []
        # Opens electricity prices
        with open("elpris.csv") as elpris:
            self.rows = list(csv.DictReader(elpris))
        # Picks thermostat    
        if termostat == "simple":
            self.termostat = ThermostatSimple(5)
        else:
            self.termostat = ThermostatSmart(6, self.rows)
        
        
    def decide_constants(self, door, compressor) -> float:
        """Decides what constants to use based on whether the compressor
        and/or the door is open

        Args:
            door (bool): True if open
            compressor (bool): True if on

        Returns:
            float: The two constants for the door and compressor
        """
        if door: # Døren er åben
            c_1 = 3 * (10**-5)
        else: # Døren er lukket
            c_1 = 5* (10**-7)
        if compressor: # Kompr tændt
            c_2 = 8 * (10**-6)
        else: # Kompr slukket
            c_2 = 0
        return c_1, c_2
    
    
    def decide_door(self, percentage=0.1) -> bool:
        """Decides whether the door to the cooler is open

        Args:
            percentage (float, optional): Percentage change for the door to be open (10%). Defaults to 0.1.

        Returns:
            _type_: bool
        """
        return random.random() <= percentage
        
            
    def get_new_temperature(self) -> float:
        """Handles the temperature and moving the discrete time by 5 min

        Returns:
            _type_: new temperature
            """
        self.temps.append(self.t_current)
        self.door_open = self.decide_door()
        self.compressor_on = self.termostat.update_compressor(self.t_current, self.n)    
        c_1, c_2, = self.decide_constants(self.door_open, self.compressor_on)
        
        new_temp = self.t_current + (
            c_1* (self.t_rum-self.t_current) + 
            c_2 * (self.t_komp - self.t_current)) * self.delta_t
        self.t_current = new_temp
        self.n += 1
        return new_temp
    
    def calculate_food_waste(self) -> None:
        """Calculates the food wasted if any and adds to a list for a total count pr. day
        """
        if self.t_current < 3.5:
            self.food_waste.append(4.39 * math.exp(-0.49*self.t_current))
        elif self.t_current > 6.5:
            self.food_waste.append(0.11 * math.exp(0.31*self.t_current))
        else:
            self.food_waste.append(0)
            
    def calculate_electricity_price(self) -> None:
        """Calculates the price for electricity if the compressor is on and adds it to a list for a total count pr. day
        """
        if self.compressor_on:
            self.electicity_cost.append(float(self.rows[self.n]['Pris']))
        else:
            self.electicity_cost.append(0)
                
    def sum_up_cost(self) -> int:
        """Sums up the cost of the electricity and food waste
        """
        return {
            "temperature_log": self.temps,
            "electricity_log": self.electicity_cost,
            "food_waste_log": self.food_waste,
            "total_cost": sum(self.electicity_cost) + sum(self.food_waste),
        }
            
    def main(self):
        self.calculate_food_waste()
        self.calculate_electricity_price()
        self.get_new_temperature()
   
    
    def run_simulation(self):
        for n in range(8640):
            self.main()
        return self.sum_up_cost()

        


if __name__ == "__main__":
    KØL = Kølerum(termostat="smart")
    for n in range(8640):
        KØL.main()
    #print(KØL.sum_up_cost())
    #print(KØL.temps)
    #print(KØL.general_cost)

