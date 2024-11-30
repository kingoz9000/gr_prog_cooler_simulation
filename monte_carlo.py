"""Dette modul styrer Monte Carlo-simuleringen af kølerummet og bliver brugt i plotter.

    Returns:
        dict: Samlede resultater af simuleringen for months måneder.
"""

from kølerum import Kølerum


class MonteCarlo:
    def __init__(self, kølerum, progress_bar=None):
        """Initializes the Monte Carlo simulation.

        Args:
            kølerum (class): En instans af Kølerum med et termostat.
            progress_bar (sg.ProgressBar, optional): En progress bar for at vise fremdrift. Defaults to None.
        Examples:
            >>> from kølerum import Kølerum
            >>> mc = MonteCarlo(kølerum=Kølerum(thermostat=None, energy_prices=[]))
            >>> isinstance(mc.kølerum_template, Kølerum)
            True
        """
        self.kølerum_template = kølerum # Kølerummet

        self.progress_bar = progress_bar # Progress bar for at vise fremdrift
        
    def run_simulation(self, months=12):
        """Kører simuleringen for et antal måneder.

        Args:
            months (int, optional): how many months to simulate Defaults to 12.

        Returns:
            dict: collected data from the simulation
        """
        self.temperature_logs = [0 for i in range(months)] # Temperaturlog for hele simuleringen
        self.electricity_logs = [0 for i in range(months)] # Elforbrugslog for hele simuleringen
        self.food_waste_logs = [0 for i in range(months)] # Madspildslog for hele simuleringen
        self.monthly_total_costs = [0 for i in range(months)] # Samlet pris for hele simuleringen
        for month in range(months):
            kølerum = Kølerum(thermostat=self.kølerum_template.termostat, energy_prices=self.kølerum_template.energy_prices) 

            month_data = kølerum.run_simulation() # Kører simuleringen for en måned

            # Samler dataen for hele simuleringen
            self.temperature_logs[month] = month_data["temperature_log"]
            self.electricity_logs[month] = month_data["electricity_log"]
            self.food_waste_logs[month] = month_data["food_waste_log"]
            self.monthly_total_costs[month] = month_data["total_cost"]
            
            # Giver fremdrift til progress bar
            if self.progress_bar:
                self.progress_bar.UpdateBar((month + 1) * 100 // months)
        return {
            "temperature_logs": self.temperature_logs,
            "electricity_logs": self.electricity_logs,
            "food_waste_logs": self.food_waste_logs,
        }
        


if __name__ == "__main__":
    """Kører en test af Monte Carlo-simuleringen."""
    import csv
    from termostat import ThermostatSemiSmart
    import doctest
    with open("elpris.csv") as elpris:
        energy_prices = list(csv.DictReader(elpris))

    monte_carlo = MonteCarlo(Kølerum(ThermostatSemiSmart(energy_prices), energy_prices))
    
    print(monte_carlo.run_simulation(1)) # Mere data
    print(doctest.testmod())
    
