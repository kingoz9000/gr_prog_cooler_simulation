import matplotlib.pyplot as plt
from monte_carlo import MonteCarlo


class CoolingPlotter:
    def __init__(self, months=10):
        # Run simulations
        mc_simple = MonteCarlo()
        self.simple_data = mc_simple.run_simulation("simple", months)

        mc_smart = MonteCarlo()
        self.smart_data = mc_smart.run_simulation("smart", months)

        self.timer = [i / 12 for i in range(len(self.simple_data["temperature_logs"][0][:7 * 24 * 2]))]
        self.prepare_weekly_data()
        self.prepare_monthly_data()

    def prepare_weekly_data(self):
        """Extracts weekly data for temperature, electricity, and food waste."""
        self.weekly_data = {
            "simple": {
                "temperature": self.simple_data["temperature_logs"][0][:7 * 24 * 2],
                "electricity": self.simple_data["electricity_logs"][0][:7 * 24 * 2],
                "food_waste": self.simple_data["food_waste_logs"][0][:7 * 24 * 2],
            },
            "smart": {
                "temperature": self.smart_data["temperature_logs"][0][:7 * 24 * 2],
                "electricity": self.smart_data["electricity_logs"][0][:7 * 24 * 2],
                "food_waste": self.smart_data["food_waste_logs"][0][:7 * 24 * 2],
            }
        }

    def prepare_monthly_data(self):
        """Calculates total costs per month for electricity and food waste."""
        self.total_cost = {
            "simple": sum(
                e + f
                for e, f in zip(
                    self.simple_data["electricity_logs"][0],
                    self.simple_data["food_waste_logs"][0],
                )
            ),
            "smart": sum(
                e + f
                for e, f in zip(
                    self.smart_data["electricity_logs"][0],
                    self.smart_data["food_waste_logs"][0],
                )
            ),
        }

    def plot_weekly_data(self, mode="together", data_type="electricity"):
        """
        Plots weekly data for either simple, smart, or both thermostats.
        mode: 'simple', 'smart', or 'together'
        data_type: 'electricity', 'food_waste', or 'temperature'
        """
        plt.figure(figsize=(10, 5))

        if mode in ["simple", "together"]:
            plt.plot(
                self.timer,
                self.weekly_data["simple"][data_type],
                label="Simple Thermostat",
                color="blue",
            )
        if mode in ["smart", "together"]:
            plt.plot(
                self.timer,
                self.weekly_data["smart"][data_type],
                label="Smart Thermostat",
                color="orange",
            )

        # Add labels
        plt.title(f"Weekly {data_type.capitalize()} ({mode.capitalize()})")
        plt.xlabel("Time (hours)")
        plt.ylabel(f"{data_type.capitalize()} (DKK)" if data_type != "temperature" else "Temperature (°C)")
        plt.legend()
        plt.grid()
        plt.tight_layout()
        plt.show()

    def plot_total_cost_histogram(self, mode="together"):
        """
        Plots histograms of total costs for simple, smart, or both thermostats.
        """
        plt.figure(figsize=(10, 5))

        if mode in ["simple", "together"]:
            plt.hist(
                [e + f for e, f in zip(
                    self.simple_data["electricity_logs"][0],
                    self.simple_data["food_waste_logs"][0],
                )],
                bins=30,
                alpha=0.7,
                color="blue",
                edgecolor="black",
                label="Simple",
            )
        if mode in ["smart", "together"]:
            plt.hist(
                [e + f for e, f in zip(
                    self.smart_data["electricity_logs"][0],
                    self.smart_data["food_waste_logs"][0],
                )],
                bins=30,
                alpha=0.7,
                color="orange",
                edgecolor="black",
                label="Smart",
            )

        # Add total cost labels
        if mode in ["simple", "together"]:
            plt.text(
                0.95,
                0.95,
                f"Total Simple: {self.total_cost['simple']:.2f} DKK",
                color="blue",
                transform=plt.gca().transAxes,
                fontsize=10,
                verticalalignment="top",
                horizontalalignment="right",
            )
        if mode in ["smart", "together"]:
            plt.text(
                0.95,
                0.90,
                f"Total Smart: {self.total_cost['smart']:.2f} DKK",
                color="orange",
                transform=plt.gca().transAxes,
                fontsize=10,
                verticalalignment="top",
                horizontalalignment="right",
            )

        plt.title("Histogram of Total Costs")
        plt.xlabel("Cost (DKK)")
        plt.ylabel("Frequency")
        plt.legend()
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    plotter = CoolingPlotter()

    # Plot electricity costs for both thermostats
    plotter.plot_weekly_data(mode="together", data_type="electricity")

    # Plot food waste for smart thermostat only
    plotter.plot_weekly_data(mode="smart", data_type="food_waste")

    # Plot temperatures for simple thermostat only
    plotter.plot_weekly_data(mode="simple", data_type="temperature")

    # Plot total cost histograms for both
    plotter.plot_total_cost_histogram(mode="together")
