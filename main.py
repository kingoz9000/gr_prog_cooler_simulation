# -*- coding: utf-8 -*-
"""
Dette er main filen for kølerums simuleringen.
@template: Tobias Kallehauge
"""

import csv
import threading

# import various funtions from matplotlib
import matplotlib
import matplotlib.pyplot as plt
import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from dataframes import CoolingPlotter
from kølerum import Kølerum
from monte_carlo import MonteCarlo
from termostat import ThermostatSemiSmart, ThermostatSimple, ThermostatSmart

# =============================================================================
# Setup some helper funtioncs for plotting
# =============================================================================

with open("elpris.csv") as elpris:
    energy_prices = list(csv.DictReader(elpris))
# Use the TkAgg backend for embedding matplotlib plots in the GUI
matplotlib.use("TkAgg")

# =============================================================================
# Helper Functions
# =============================================================================


def draw_figure(canvas, figure):
    """
    Embeds a matplotlib figure into a PySimpleGUI canvas.
    """
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg


def delete_fig(fig):
    """
    Deletes a matplotlib figure from the GUI canvas.
    """
    fig.get_tk_widget().forget()
    plt.close("all")


# =============================================================================
# GUI Layout and Main Loop
# =============================================================================


layout1 = [
    [sg.Text("Vælg antal måneder")],
    [sg.Combo(["10", "100", "1000", "10000"], default_value="10", key="N")],
    [sg.Text("Vælg termostat type")],
    [sg.Combo(["semi smart", "smart"], default_value="smart", key="THERMOSTAT")],
    [sg.Button("Kør Simulering", key="-KØR-")],
]

# Define the GUI layout


window1 = sg.Window(
    "Kølerums Simulering",
    layout=layout1,
    finalize=True,
    size=(1200, 1000),
    element_justification="center",
)


# Variable to track the currently displayed figure
fig_gui = None
cooling_plotter = None


def create_cooling_plotter(N, thermostat_type, progress_bar):
    global cooling_plotter
    if thermostat_type == "semi smart":
        kølerum_simple = Kølerum(
            thermostat=ThermostatSimple(energy_prices), energy_prices=energy_prices
        )
        kølerum_smart = Kølerum(
            thermostat=ThermostatSemiSmart(energy_prices), energy_prices=energy_prices
        )
    elif thermostat_type == "smart":
        kølerum_simple = Kølerum(
            thermostat=ThermostatSimple(energy_prices), energy_prices=energy_prices
        )
        kølerum_smart = Kølerum(
            thermostat=ThermostatSmart(energy_prices), energy_prices=energy_prices
        )

    cooling_plotter = CoolingPlotter(
        N, progress_bar, kølerum_simple, kølerum_smart, MonteCarlo
    )


while True:
    event, values = window1.read()
    if event == sg.WIN_CLOSED:
        break
    if event == "-KØR-":

        N = int(values["N"])
        thermostat_type = values["THERMOSTAT"]
        # Create a loading bar window
        layout_loading = [
            [sg.Text("Loading...")],
            [sg.ProgressBar(100, orientation="h",
                            size=(20, 20), key="-PROG-")],
        ]
        window_loading = sg.Window("Loading", layout_loading, finalize=True)
        progress_bar = window_loading["-PROG-"]

        # Start the CoolingPlotter creation in a separate thread
        thread = threading.Thread(
            target=create_cooling_plotter, args=(
                N, thermostat_type, progress_bar)
        )
        thread.start()
        window1.close()
        # Update the progress bar while the thread is running
        while thread.is_alive():
            event, _ = window_loading.read(timeout=100)
            if event == sg.WIN_CLOSED:
                break

        window_loading.close()
        layout2 = [
            [
                sg.Text(
                    "Cooling Plotter GUI",
                    font=("Helvetica", 18),
                    justification="center",
                )
            ],
            [
                sg.Frame(
                    "Gennemsnitlige Priser",
                    layout=[
                        [
                            sg.Text(
                                f"Simple gennemsnitlig pris: {
                                    cooling_plotter.df_data_simple_average:.2f} DKK",
                                font=("Helvetica", 14),
                                background_color="lightblue",
                                pad=(10, 5),
                            )
                        ],
                        [
                            sg.Text(
                                f"Smart gennemsnitlig pris: {
                                    cooling_plotter.df_data_smart_average:.2f} DKK",
                                font=("Helvetica", 14),
                                background_color="lightgreen",
                                pad=(10, 5),
                            )
                        ],
                    ],
                    font=("Helvetica", 16),
                    title_color="blue",
                    pad=(20, 10),
                )
            ],
            [sg.Button("Akkumuleret elforbrug",
                       key="-CUMSUM-", size=(30, 2)), sg.Combo(["Dag", "Uge", "Måned"], default_value="Uge", key="ELDURATION")],
            [
                sg.Button("Temperatur (Simple)",
                          key="-TEMP_SIMPLE-", size=(20, 2)),
                sg.Button("Temperatur (Smart)",
                          key="-TEMP_SMART-", size=(20, 2)),
            sg.Combo(["Dag", "Uge"], default_value="Dag", key="TEMPDURATION")],
            [sg.Button("Histogram", key="-HISTOGRAM-", size=(20, 2))],
            [sg.Canvas(key="-CANVAS-", size=(1000, 600))],
        ]

        window2 = sg.Window(
            "Kølerums Simulering",
            layout=layout2,
            size=(1200, 1000),
            finalize=True,
            element_justification="center",
        )

        while True:
            event, values = window2.read()

            # Exit the loop if the window is closed
            if event == sg.WIN_CLOSED:
                break
                # Handle plotting events
            if event in ("-CUMSUM-", "-TEMP_SIMPLE-", "-TEMP_SMART-", "-HISTOGRAM-"):
                # Delete the previous figure, if any
                if fig_gui:
                    delete_fig(fig_gui)

                # Generate the appropriate plot
                if event == "-CUMSUM-":
                    el_duration = values["ELDURATION"]
                    if el_duration == "Uge":
                        fig = cooling_plotter.plot_weekly_electricity_cumsum(
                            duration="week"
                        )
                    elif el_duration == "Dag":
                        fig = cooling_plotter.plot_weekly_electricity_cumsum(
                            duration="day"
                        )
                    else:
                        fig = cooling_plotter.plot_weekly_electricity_cumsum(
                            duration="month"
                        )
                elif event == "-TEMP_SIMPLE-":
                    temp_duration = values["TEMPDURATION"]
                    if temp_duration == "Uge":
                        fig = cooling_plotter.plot_temperature(
                            duration="week", type="simple"
                        )
                    else:
                        fig = cooling_plotter.plot_temperature(
                        duration="day", type="simple"
                    )
                elif event == "-TEMP_SMART-":
                    temp_duration = values["TEMPDURATION"]
                    if temp_duration == "Uge":
                        fig = cooling_plotter.plot_temperature(
                            duration="week", type="smart"
                        )
                    else:
                        fig = cooling_plotter.plot_temperature(
                        duration="day", type="smart"
                    )
                elif event == "-HISTOGRAM-":
                    fig = cooling_plotter.plot_histogram_cost()

                # Embed the new plot into the GUI
                fig_gui = draw_figure(window2["-CANVAS-"].TKCanvas, fig)

# Close the GUI and clean up
plt.close("all")
window2.close()
