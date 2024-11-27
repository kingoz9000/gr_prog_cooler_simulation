from kølerum import Kølerum
from termostat import ThermostatSimple, ThermostatSmart
class MonteCarlo:
    def __init__(self, kølerum):
        """
        Initializes the Monte Carlo simulation with a provided Kølerum instance.

        Args:
            kølerum (Kølerum): An initialized Kølerum object with the desired thermostat.
        """
        self.kølerum_template = kølerum
        self.temperature_logs = []
        self.electricity_logs = []
        self.food_waste_logs = []
        self.monthly_total_costs = []

    def run_simulation(self, months=12):
        """
        Runs the simulation for the specified number of months.

        Args:
            months (int): Number of months to simulate.

        Returns:
            dict: Aggregated simulation results.
        """
        for _ in range(months):
            # Reinitialize Kølerum for each month
            kølerum = Kølerum(thermostat=self.kølerum_template.termostat)

            # Run simulation for one month
            month_data = kølerum.run_simulation()

            # Aggregate results
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
    # Create instances of the thermostats
    simple_thermostat = ThermostatSimple(t_target=5)
    smart_thermostat = ThermostatSmart(t_target=6)

    # Create Kølerum objects with the respective thermostats
    kølerum_simple = Kølerum(thermostat=simple_thermostat)
    kølerum_smart = Kølerum(thermostat=smart_thermostat)

    # Initialize Monte Carlo simulations
    mc_simple = MonteCarlo(kølerum_simple)
    mc_smart = MonteCarlo(kølerum_smart)

    # Run simulations for 12 months
    simple_data = mc_simple.run_simulation(months=12)
    smart_data = mc_smart.run_simulation(months=12)

    # Print aggregated results
    print("Simple Data:", simple_data)
    print("Smart Data:", smart_data)

