import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from kølerum import Kølerum
from monte_carlo import MonteCarlo
from termostat import ThermostatSimple, ThermostatSmart


class CoolingPlotter:
    def __init__(self, months=10):
        """Prepare data for plotting."""
        mc_simple = MonteCarlo(Kølerum(thermostat=ThermostatSimple()))
        mc_smart = MonteCarlo(Kølerum(thermostat=ThermostatSmart()))

        self.simple_data = mc_simple.run_simulation(months)
        self.smart_data = mc_smart.run_simulation(months)

        self.df_data_simple = pd.DataFrame(self.simple_data)
        self.df_data_smart = pd.DataFrame(self.smart_data)

        num_steps = len(self.df_data_simple["electricity_logs"][0])

        self.x_hours = np.arange(num_steps) / 12

    def plot_weekly_electricity(self, type="simple"):
        """Return a figure for weekly electricity consumption."""
        fig, ax = plt.subplots()
        if type == "simple":
            ax.plot(self.df_data_simple["electricity_logs"][0][:2160], label="Simple")
        else:
            ax.plot(self.df_data_smart["electricity_logs"][0][:2160], label="Smart")

        ax.set_title("Weekly Electricity Consumption")
        ax.set_xlabel("Timet")
        ax.set_ylabel("Electricity (kWh)")
        ax.legend()
        return fig

    def plot_weekly_electricity_cumsum(self, duration="week"):
        """Return a figure for cumulative electricity consumption."""
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
        else:
            raise ValueError("Invalid duration. Use 'day' or 'week'.")

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

    def plot_weekly_temperature(self, duration="week", type="simple"):
        """Return a figure for weekly temperature."""
        simple_data_temperature = np.asarray(self.df_data_simple["temperature_logs"][0])
        smart_data_temperature = np.asarray(self.df_data_smart["temperature_logs"][0])

        if duration == "day":
            end_index = 24 * 12  # 60/5 = 12
            title = "Temperaturændringer over én dag"
        elif duration == "week":
            end_index = 24 * 12 * 7
            title = "Temperaturændringer over en uge"
        else:
            raise ValueError("Invalid duration. Use 'day' or 'week'.")

        fig, ax = plt.subplots()
        if type == "simple":
            ax.plot(self.x_hours[:end_index], simple_data_temperature[:end_index])
        elif type == "smart":
            ax.plot(self.x_hours[:end_index], smart_data_temperature[:end_index])
        else:
            raise ValueError("Invalid type. Use 'simple' or 'smart'.")

        ax.set_title(title + f" ({type.capitalize()})")
        ax.set_xlabel("Time (hours)")
        ax.set_ylabel("Temperature (°C)")
        ax.grid(True)
        return fig

    def plot_histogram_cost(self):
        """Return a figure for the histogram of costs."""
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

        fig, ax = plt.subplots()
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
