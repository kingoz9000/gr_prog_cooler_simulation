import random
from termostat import ThermostatSimple
import math
import csv


class Kølerum:
    def __init__(self, termostat):
        self.t_rum = 20
        self.t_komp = -5
        self.delta_t = 300
        self.t_start = 5
        self.t_target = 5
        
        self.t_current = self.t_start
        self.door_open = False
        self.compressor_on = False
        self.termostat = termostat
        
        self.n = 0
        self.food_waste = []
        self.temps = []
        self.electicity_cost = []
        self.general_cost = []
        with open("elpris.csv") as elpris:
            self.rows = list(csv.DictReader(elpris))
        
        
    def decide_constants(self, door, compressor):
        if door: # Døren er åben
            c_1 = 3 * (10**-5)
        else: # Døren er lukket
            c_1 = 5* (10**-7)
        if compressor: # Kompr tændt
            c_2 = 8 * (10**-6)
        else: # Kompr slukket
            c_2 = 0
        return c_1, c_2
    
    
    def decide_door(self, percentage=0.1):
        return random.random() <= percentage
        
            
    def get_new_temperature(self):
        self.temps.append(self.t_current)
        self.door_open = self.decide_door()
        self.compressor_on = self.termostat.update_compressor(self.t_current)
        c_1, c_2, = self.decide_constants(self.door_open, self.compressor_on)
        
        new_temp = self.t_current + (
            c_1* (self.t_rum-self.t_current) + 
            c_2 * (self.t_komp - self.t_current)) * self.delta_t
        self.t_current = new_temp
        self.n += 1
        return new_temp
    
    
    def calculate_food_waste(self):
        if self.t_current < 3.5:
            self.food_waste.append(4.39 * math.exp(-0.49*self.t_current))
        elif self.t_current > 6.5:
            self.food_waste.append(0.11 * math.exp(0.31*self.t_current))
        else:
            self.food_waste.append(0)
            
            
    def calculate_electricity_price(self):
            if self.compressor_on:
                self.electicity_cost.append(float(self.rows[self.n]['Pris']))
            else:
                self.electicity_cost.append(0)
                
            
    def main(self):
        self.calculate_food_waste()
        self.calculate_electricity_price()
        self.get_new_temperature()
   
    
        

        


if __name__ == "__main__":
    KØL = Kølerum(ThermostatSimple(5))
    for n in range(8640):
        KØL.main()
    print(KØL.temps)
    print(KØL.food_waste)
    print(KØL.electicity_cost)
