# -*- coding: utf-8 -*-
"""
Dette er main filen for kølerums simuleringen med en GUI. Der er brugt template 
og koden er en smule rodet og ikke optimeret.
@template: Tobias Kallehauge
"""

import csv
import threading


import matplotlib
import matplotlib.pyplot as plt
import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from plotter import CoolingPlotter
from kølerum import Kølerum
from monte_carlo import MonteCarlo
from termostat import ThermostatSemiSmart, ThermostatSimple, ThermostatSmart



# Indlæser elpriserne
with open("elpris.csv") as elpris:
    energy_prices = list(csv.DictReader(elpris))

matplotlib.use("TkAgg")




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


# Lauyout til første vindue
layout1 = [
    [sg.Text("Vælg antal måneder")],
    [sg.Combo(["10", "100", "1000", "10000"], default_value="10", key="N")],
    [sg.Text("Vælg termostat type")],
    [sg.Combo(["semi smart", "smart"], default_value="smart", key="THERMOSTAT")],
    [sg.Button("Kør Simulering", key="-KØR-")],
    [
                sg.Frame(
                    "Denne simulering",
                    layout=[
                        [
                            sg.Text(
                                f"Denne simulering har to termostater, et semi-smart og et smart. ",
                                font=("Helvetica", 14),
                                pad=(10, 5),
                            )
                        ],
                        [
                            sg.Text(
                                f"Det semi-smarte termostat har en måltemperatur på 6.4 grader.",
                                font=("Helvetica", 14),
                                pad=(10, 5),
                            )
                        ],
                        [
                            sg.Text(
                                f"Det smarte termostat har en måltemperatur på 6.2 grader og en lavere grænse på 3 grader.",
                                font=("Helvetica", 14),
                                pad=(10, 5),
                            )
                        ],
                        [
                            sg.Text(
                                f"Uderover dette har tænder termostatet altid når prisen er på 2 DKK så længde den er under halvejs i måneden",
                                font=("Helvetica", 14),
                                pad=(10, 5),
                            )
                        ],                       
                        [
                            sg.Text(
                                f"OBS simuleringen bliver kørt for både det simple og det smarte/semi-smarte termostat.",
                                font=("Helvetica", 14),
                                pad=(10, 5),
                            )
                        ],
                        [
                            sg.Text(
                                f"Koden er heller ikke optimeret så i skal have rigtig god tid hvis i vælger høje N.",
                                font=("Helvetica", 14),
                                pad=(10, 5),
                             )
                        ],
                    ],
                    font=("Helvetica", 16),
                    title_color="blue",
                    pad=(20, 10),
                    )   
            ],
    ]   


# Første vindue setup
window1 = sg.Window(
    "Kølerums Simulering",
    layout=layout1,
    finalize=True,
    size=(1200, 1000),
    element_justification="center",
)

# Fra template
fig_gui = None
cooling_plotter = None


def create_cooling_plotter(N, thermostat_type, progress_bar):
    """Bestemmer hvilken termostat der skal bruges og kører simuleringen.

    Args:
        N (int): Antal simulationer
        thermostat_type (str): Hviket termostat der skal bruges
        progress_bar (sg.ProgressBar): Bare en loading bar der skal have fremdrift af monte carlo
    """
    global cooling_plotter # Gad ikke putte alt i en klasse når det er gui
    # Forskellige termostater
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
    # Kører simuleringen
    cooling_plotter = CoolingPlotter(
        N, progress_bar, kølerum_simple, kølerum_smart, MonteCarlo
    )

# Main loop 1
while True:
    # Første vindue
    event, values = window1.read()
    if event == sg.WIN_CLOSED:
        exit()
    
    if event == "-KØR-":
        N = int(values["N"])
        thermostat_type = values["THERMOSTAT"]
        # Loading bar
        layout_loading = [
            [sg.Text("Loading...")],
            [sg.ProgressBar(100, orientation="h",
                            size=(20, 20), key="-PROG-")],
        ]
        window_loading = sg.Window("Loading", layout_loading, finalize=True)
        progress_bar = window_loading["-PROG-"]

        # Kører simulation i en anden thread
        thread = threading.Thread(
            target=create_cooling_plotter, args=(
                N, thermostat_type, progress_bar)
        )
        thread.start()
        window1.close()
        # Opdaterer loading bar
        while thread.is_alive():
            event, _ = window_loading.read(timeout=100)
            if event == sg.WIN_CLOSED:
                exit()
        # Endelig færdig:)
        window_loading.close()
        # Layout til andet vindue
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
                                f"Simple gennemsnitlig pris: {cooling_plotter.df_data_simple_average:.2f} DKK",
                                font=("Helvetica", 14),
                                pad=(10, 5),
                            )
                        ],
                        [
                            sg.Text(
                                f"Smart gennemsnitlig pris: {cooling_plotter.df_data_smart_average:.2f} DKK",
                                font=("Helvetica", 14),
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
                       key="-CUMSUM-", size=(30, 2)), 
             sg.Button("Akkumuleret madspild",
                       key="-FOODCUMSUM-", size=(30, 2)), 
             sg.Combo(["Dag", "Uge", "Måned"], default_value="Uge", key="ELDURATION")],
            
            [
                sg.Button("Temperatur (Simple)",
                          key="-TEMP_SIMPLE-", size=(20, 2)),
                sg.Button("Temperatur (Smart)",
                          key="-TEMP_SMART-", size=(20, 2)),
            sg.Combo(["Dag", "Uge"], default_value="Dag", key="TEMPDURATION")],

            [sg.Button("Histogram", key="-HISTOGRAM-", size=(20, 2))],
            [sg.Canvas(key="-CANVAS-", size=(1000, 600))],
        ]

        # Andet vindue setup
        window2 = sg.Window(
            "Kølerums Simulering",
            layout=layout2,
            size=(1200, 1000),
            finalize=True,
            element_justification="center",
        )

        # Main loop 2
        while True:
            event, values = window2.read()
            if event == sg.WIN_CLOSED:
                break
            
            # Plots
            if event in ("-CUMSUM-", "-TEMP_SIMPLE-", "-TEMP_SMART-", "-HISTOGRAM-", "-FOODCUMSUM-"):
                if fig_gui:
                    delete_fig(fig_gui)

                # Alle de forskellige plots med forskellige intervaller
                if event == "-CUMSUM-":
                    el_duration = values["ELDURATION"]
                    if el_duration == "Uge":
                        fig = cooling_plotter.plot_electricity_cumsum(
                            duration="week"
                        )
                    elif el_duration == "Dag":
                        fig = cooling_plotter.plot_electricity_cumsum(
                            duration="day"
                        )
                    else:
                        fig = cooling_plotter.plot_electricity_cumsum(
                            duration="month"
                        )
                elif event == "-FOODCUMSUM-":
                    el_duration = values["ELDURATION"]
                    if el_duration == "Uge":
                        fig = cooling_plotter.plot_food_waste_cumsum(
                            duration="week"
                        )
                    elif el_duration == "Dag":
                        fig = cooling_plotter.plot_food_waste_cumsum(
                            duration="day"
                        )
                    else:
                        fig = cooling_plotter.plot_food_waste_cumsum(
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

                # Fra template
                fig_gui = draw_figure(window2["-CANVAS-"].TKCanvas, fig)

plt.close("all")
window2.close()
