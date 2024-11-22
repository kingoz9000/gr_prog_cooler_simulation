from kølerum import Kølerum
from termostat import ThermostatSimple


class MonteCarlo:
    def __init__(self, number_of_simulations, termostat):
        self.N = number_of_simulations
        self.termostat = termostat

    def run_simulation(self):
        KØL = Kølerum(self.termostat)
        for _ in range(self.N):
            KØL.main()
        temp = KØL.temps
        electricity = KØL.electicity_cost
        food_waste = KØL.food_waste
        return temp, electricity, food_waste


if __name__ == "__main__":
    temps, electricity, food_waste = MonteCarlo(
        8640, ThermostatSimple(5)
    ).run_simulation()
    # print(f"Temps: {temps}")
    # print(f"Electricity: {electricity}")
    # print(f"Food Waste: {food_waste}")
    print(f"Sum of all costs in Septemper 2022: {
          sum(electricity)+sum(food_waste)},-")
