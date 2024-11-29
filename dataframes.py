"""Dette modul styrer data for plottene.

    Raises:
        ValueError: Hvis duration ikke er 'day' eller 'week'.
        ValueError: Hvis type ikke er 'simple' eller 'smart'.

    Returns:
       class : En instans af CoolingPlotter.
"""

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


class CoolingPlotter:
    def __init__(self, months=10, progress_bar=None, kølerum_simple=None, kølerum_smart=None, monte_carlo_class=None):
        """Forbereder data til plottene.

        Args:
            months (int, optional): amount of months to simulate. Defaults to 10.
            progress_bar (sg.ProgressBar, optional): to track progress of the simulation. Defaults to None.
            monte_carlo_class (class, optional): an instance of the montecarlo class. Defaults to None.
        """

        mc_simple = monte_carlo_class(
            kølerum_simple, progress_bar)  # Monte Carlo for simple
        mc_smart = monte_carlo_class(
            kølerum_smart, progress_bar)  # Monte Carlo for smart

        self.simple_data = mc_simple.run_simulation(
            months)  # Simulerer for simple
        self.smart_data = mc_smart.run_simulation(
            months)  # Simulerer for smart

        self.df_data_simple = pd.DataFrame(
            self.simple_data)  # Dataframe for simple
        self.df_data_smart = pd.DataFrame(
            self.smart_data)  # Dataframe for smart

        self.df_data_simple_average = (
            self.df_data_simple["electricity_logs"].apply(sum).mean() +
            self.df_data_simple["food_waste_logs"].apply(sum).mean()
        )

        self.df_data_smart_average = (
            self.df_data_smart["electricity_logs"].apply(sum).mean() +
            self.df_data_smart["food_waste_logs"].apply(sum).mean()
        )

        # Antal steps
        num_steps = len(self.df_data_simple["electricity_logs"][0])

        # Ville gerne have dataet vist i steps af timer da dette er mere overskueligt
        self.x_hours = np.arange(num_steps) / 12

    def plot_weekly_electricity(self, type="simple"):
        """Retunerer et plot for ugentlig elforbrug.

        Args:
            type (str, optional): simple or smart thermostat. Defaults to "simple".

        Returns:
            fig: figure for the plot
        """
        fig, ax = plt.subplots()
        if type == "simple":
            ax.plot(
                self.df_data_simple["electricity_logs"][0][:2160], label="Simple")
        else:
            ax.plot(self.df_data_smart["electricity_logs"]
                    [0][:2160], label="Smart")

        ax.set_title("Weekly Electricity Consumption")
        ax.set_xlabel("Timet")
        ax.set_ylabel("Electricity (kWh)")
        ax.legend()
        return fig

    def plot_weekly_electricity_cumsum(self, duration="week"):
        """Returnerer et plot for akkumuleret elforbrug for en uge eller dag

        Args:
            duration (str, optional): week or day. Defaults to "week".

        Raises:
            ValueError: If duration is not 'day' or 'week'.

        Returns:
            fig: a figure for the plot
        """
        simple_data_cumsum = np.asarray(
            self.df_data_simple["electricity_logs"][0]
        ).cumsum()
        smart_data_cumsum = np.asarray(
            self.df_data_smart["electricity_logs"][0]
        ).cumsum()

        if duration == "day":
            end_index = 24 * 12
            title = "Akkumuleret elforbrug over én dag"
        elif duration == "week":
            end_index = 24 * 12 * 7
            title = "Akkumuleret elforbrug over en uge(168 timer)"
        elif duration == "month":
            end_index = 24 * 12 * 30
            title = "Akkumuleret elforbrug over en måned"
        else:
            raise ValueError("Invalid duration. Use 'day', 'week' or 'month'.")

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(
            self.x_hours[:end_index],
            simple_data_cumsum[:end_index],
            label="Simple",
            linewidth=2,
            color="blue",
        )
        ax.plot(
            self.x_hours[:end_index],
            smart_data_cumsum[:end_index],
            label="Smart",
            linewidth=2,
            color="orange",
            linestyle="--",
        )
        # Calculate totals
        total_simple = simple_data_cumsum[end_index - 1]
        total_smart = smart_data_cumsum[end_index - 1]

        # Add totals as text in the top-right corner
        ax.text(
            0.95,
            0.95,
            f"Total (Simple): {total_simple:.2f}\nTotal (Smart): {
                total_smart:.2f}",
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment="top",
            horizontalalignment="right",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
        )
        ax.set_title(title)
        ax.set_xlabel("Timer")
        ax.set_ylabel("Akkumuleret elforbrug")
        ax.legend(loc="upper left")
        ax.grid(True, linestyle="--", alpha=0.7)
        return fig

    def plot_temperature(self, duration="week", type="simple"):
        """Returnerer et plot for temperaturændringer over en dag eller uge.

        Args:
            duration (str, optional): week or day. Defaults to "week".
            type (str, optional): thermostat. Defaults to "simple".

        Raises:
            ValueError: If duration is not 'day' or 'week'.
            ValueError: If type is not 'simple' or 'smart'.

        Returns:
            fig: a figure for the plot
        """
        simple_data_temperature = np.asarray(
            self.df_data_simple["temperature_logs"][0])
        smart_data_temperature = np.asarray(
            self.df_data_smart["temperature_logs"][0])

        if duration == "day":
            end_index = 24 * 12  # 60/5 = 12
            title = "Temperaturændringer over én dag"
        elif duration == "week":
            end_index = 24 * 12 * 7
            title = "Temperaturændringer over en uge"
        else:
            raise ValueError("Invalid duration. Use 'day' or 'week'.")

        fig, ax = plt.subplots(figsize=(10, 6))
        if type == "simple":
            ax.plot(self.x_hours[:end_index],
                    simple_data_temperature[:end_index])
        elif type == "smart":
            ax.plot(self.x_hours[:end_index],
                    smart_data_temperature[:end_index])
        else:
            raise ValueError("Invalid type. Use 'simple' or 'smart'.")

        ax.set_title(title + f" ({type.capitalize()})")
        ax.set_xlabel("Time (hours)")
        ax.set_ylabel("Temperature (°C)")
        ax.grid(True)
        return fig

    def plot_histogram_cost(self):
        """Returnerer et histogram for totalpris for en måned.

        Returns:
            fig: a figure for the plot
        """
        simple_costs = [
            e + f
            for e, f in zip(
                self.df_data_simple["electricity_logs"][0],
                self.df_data_simple["food_waste_logs"][0],
            )
        ]
        smart_costs = [
            e + f
            for e, f in zip(
                self.df_data_smart["electricity_logs"][0],
                self.df_data_smart["food_waste_logs"][0],
            )
        ]

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(simple_costs, bins=30, alpha=0.7, color="blue", label="Simple")
        ax.hist(smart_costs, bins=30, alpha=0.7, color="orange", label="Smart")
        total_simple = sum(simple_costs)
        total_smart = sum(smart_costs)
        mean_simple = total_simple / len(simple_costs)
        mean_smart = total_smart / len(smart_costs)

        ax.text(
            0.95,
            0.95,
            (
                f"Simple:\n"
                f"  Total: {total_simple:.2f}\n"
                f"  Median: {mean_simple:.2f}\n\n"
                f"Smart:\n"
                f"  Total: {total_smart:.2f}\n"
                f"  Median: {mean_smart:.2f}"
            ),
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment="top",
            horizontalalignment="right",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
        )
        ax.set_title("Histogram af totalpris for en måned")
        ax.set_xlabel("DKK")
        ax.set_ylabel("Frekvens")
        ax.legend()
        ax.grid(axis="y", linestyle="--", alpha=0.7)
        return fig

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import csv
    from monte_carlo import MonteCarlo
    from kølerum import Kølerum
    from termostat import ThermostatSimple, ThermostatSemiSmart


    with open("elpris.csv") as file:
        energy_prices = list(csv.DictReader(file))

    months = 1000  


    thermostat_simple = ThermostatSimple()
    thermostat_smart = ThermostatSemiSmart()
    kølerum_simple = Kølerum(thermostat_simple, energy_prices)
    kølerum_smart = Kølerum(thermostat_smart, energy_prices)
    monte_carlo_simple = MonteCarlo(kølerum_simple) 
    monte_carlo_smart = MonteCarlo(kølerum_smart)


    plotter = CoolingPlotter(
        months=months,
        kølerum_simple=kølerum_simple,
        kølerum_smart=kølerum_smart,
        monte_carlo_class=MonteCarlo,
    )
    plotter.plot_weekly_electricity_cumsum(duration="week")
    plotter.plot_weekly_electricity_cumsum(duration="day")
    plotter.plot_weekly_electricity_cumsum(duration="month")
    plotter.plot_temperature(duration="week", type="simple")
    plotter.plot_temperature(duration="week", type="smart")
    plotter.plot_histogram_cost()
    plt.show()

