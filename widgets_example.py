from monte_carlo import MonteCarlo
import matplotlib.pyplot as plt

# Simulate for both thermostat types
mc_simple = MonteCarlo()
simple_data = mc_simple.run_simulation("simple", 10)  # 10 months

mc_smart = MonteCarlo()
smart_data = mc_smart.run_simulation("smart", 10)  # 10 months

# --- Plot 1: Weekly Temperature Time Series ---
def plot_temperature(temperature_logs, title):
    weekly_temperatures = temperature_logs[0][:7 * 24 * 2]  # First week
    time = [i * 5 for i in range(len(weekly_temperatures))]  # Time in minutes
    plt.plot(time, weekly_temperatures)
    plt.title(title)
    plt.xlabel("Time (minutes)")
    plt.ylabel("Temperature (°C)")
    plt.grid()
    plt.show()

plot_temperature(simple_data["temperature_logs"], "Simple Thermostat: Weekly Temperature")
plot_temperature(smart_data["temperature_logs"], "Smart Thermostat: Weekly Temperature")

# --- Plot 2: Expense Time Series ---
def plot_expenses(electricity_logs, food_waste_logs, title):
    weekly_electricity = electricity_logs[0][:7 * 24 * 2]  # First week
    weekly_food_waste = food_waste_logs[0][:7 * 24 * 2]
    time = [i * 5 for i in range(len(weekly_electricity))]

    plt.plot(time, weekly_electricity, label="Electricity Cost (DKK)")
    plt.plot(time, weekly_food_waste, label="Food Waste Cost (DKK)")
    plt.title(title)
    plt.xlabel("Time (minutes)")
    plt.ylabel("Cost (DKK)")
    plt.legend()
    plt.grid()
    plt.show()

plot_expenses(
    simple_data["electricity_logs"], simple_data["food_waste_logs"],
    "Simple Thermostat: Weekly Expenses"
)
plot_expenses(
    smart_data["electricity_logs"], smart_data["food_waste_logs"],
    "Smart Thermostat: Weekly Expenses"
)

# --- Plot 3: Monthly Expense Histogram ---
def plot_histogram(monthly_total_costs, title):
    plt.hist(monthly_total_costs, bins=10, edgecolor="black")
    plt.title(title)
    plt.xlabel("Monthly Expense (DKK)")
    plt.ylabel("Frequency")
    plt.grid()
    plt.show()

plot_histogram(simple_data["monthly_total_costs"], "Simple Thermostat: Monthly Expenses")
plot_histogram(smart_data["monthly_total_costs"], "Smart Thermostat: Monthly Expenses")
