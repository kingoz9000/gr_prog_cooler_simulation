from kølerum import Kølerum
from termostat import ThermostatSimple


class MonteCarlo:
    def __init__(self):
        self.temperature_logs = []  
        self.electricity_logs = []  
        self.food_waste_logs = []  
        self.monthly_total_costs = []
    
    def run_simulation(self, termostat, months):
        for _ in range(months):
            kølerum = Kølerum(termostat)
            month_data = kølerum.run_simulation()

            # Aggregate data
            self.temperature_logs.append(month_data["temperature_log"])
            self.electricity_logs.append(month_data["electricity_log"])
            self.food_waste_logs.append(month_data["food_waste_log"])
            self.monthly_total_costs.append(month_data["total_cost"])

        return {
            "temperature_logs": self.temperature_logs,
            "electricity_logs": self.electricity_logs,
            "food_waste_logs": self.food_waste_logs,
            "monthly_total_costs": self.monthly_total_costs,
        }
    
if __name__ == "__main__":
    price1 = MonteCarlo().run_simulation(Kølerum("simple"), 100)
    price2 = MonteCarlo().run_simulation(Kølerum("smart"), 100)
    #print(f"Temps: {temps}")
    #print(f"Electricity: {electricity}")
    #print(f"Food Waste: {food_waste}")
    print(price1)
    
        
