# -*- coding: utf-8 -*-
"""
Dette er main filen for kølerums simuleringen.
@template: Tobias Kallehauge
"""

from termostat import ThermostatSimple, ThermostatSemiSmart
from kølerum import Kølerum
from monte_carlo import MonteCarlo
from dataframes import CoolingPlotter
import PySimpleGUI as sg
# import various funtions from matplotlib
import matplotlib 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import threading
import csv

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
    plt.close('all')

# =============================================================================
# GUI Layout and Main Loop
# =============================================================================


layout1 = [
    [sg.Text("Vælg simuleringsdata")],
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
    size=(1200, 800),
    element_justification="center"
)




# Variable to track the currently displayed figure
fig_gui = None
cooling_plotter = None

def create_cooling_plotter(N, thermostat_type, progress_bar):
    global cooling_plotter
    print(energy_prices)
    if thermostat_type == "semi smart":
        kølerum_simple = Kølerum(thermostat=ThermostatSimple(energy_prices), energy_prices=energy_prices)
        kølerum_smart = Kølerum(thermostat=ThermostatSemiSmart(energy_prices), energy_prices=energy_prices)
    elif thermostat_type == "smart":
        kølerum_simple = Kølerum(thermostat=ThermostatSimple(energy_prices), energy_prices=energy_prices)
        kølerum_smart = Kølerum(thermostat=ThermostatSemiSmart(energy_prices), energy_prices=energy_prices)
    
    cooling_plotter = CoolingPlotter(N, progress_bar,kølerum_simple, kølerum_smart, MonteCarlo)


while True:
    event, values = window1.read()
    if event == sg.WIN_CLOSED:
        break
    if event == "-KØR-":
        
        N = int(values["N"])
        thermostat_type = values["THERMOSTAT"]
        # Create a loading bar window
        layout_loading = [[sg.Text("Loading...")], [sg.ProgressBar(100, orientation='h', size=(20, 20), key='-PROG-')]]
        window_loading = sg.Window("Loading", layout_loading, finalize=True)
        progress_bar = window_loading['-PROG-']
        
        # Start the CoolingPlotter creation in a separate thread
        thread = threading.Thread(target=create_cooling_plotter, args=(N, thermostat_type, progress_bar))
        thread.start()
        window1.close()
        # Update the progress bar while the thread is running
        while thread.is_alive():
            event, _ = window_loading.read(timeout=100)
            if event == sg.WIN_CLOSED:
                break
        
        window_loading.close()
        layout2 = [
    [sg.Text("Cooling Plotter GUI")],
    [sg.Button("Ugentlig akkumuleret elforbrug", key="-CUMSUM-")],
    [sg.Button(f"Temperatur(Simple)", key="-TEMP_SIMPLE-"), 
     sg.Button("Temperatur(Smart)", key="-TEMP_SMART-")],
    # De gennemsnitlige priser (Kan være anderledes end histogrammet der viser for en måned)
    [sg.Text(f"Simple gennemsnitlig pris: {cooling_plotter.df_data_simple_average}")],
    [sg.Text(f"Smart gennemsnitlig pris: {cooling_plotter.df_data_smart_average}")],
    [sg.Button("Histogram", key="-HISTOGRAM-")],
    [sg.Canvas(key="-CANVAS-")],
]
        window2 = sg.Window(
            "Kølerums Simulering",
            layout=layout2,
            size=(1200, 800),
            finalize=True,
            element_justification="center"
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
                    fig = cooling_plotter.plot_weekly_electricity_cumsum(duration="week")
                elif event == "-TEMP_SIMPLE-":
                    fig = cooling_plotter.plot_temperature(duration="day", type="simple")
                elif event == "-TEMP_SMART-":
                    fig = cooling_plotter.plot_temperature(duration="day", type="smart")
                elif event == "-HISTOGRAM-":
                    fig = cooling_plotter.plot_histogram_cost()

                # Embed the new plot into the GUI
                fig_gui = draw_figure(window2["-CANVAS-"].TKCanvas, fig)

# Close the GUI and clean up
plt.close('all')
window2.close()
   
