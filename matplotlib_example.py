# -*- coding: utf-8 -*-
"""
Created on Mon Nov  8 13:03:03 2021

@author: Tobias Kallehauge
"""

from termostat import ThermostatSimple, ThermostatSmart
from kølerum import Kølerum
from monte_carlo import MonteCarlo
from dataframes import CoolingPlotter
import PySimpleGUI as sg
import numpy as np
# import various funtions from matplotlib
import matplotlib 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt



# =============================================================================
# Setup some helper funtioncs for plotting
# =============================================================================


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

# Create the CoolingPlotter instance with 100 months of simulation data
cooling_plotter = CoolingPlotter(100)

# Define the GUI layout
layout = [
    [sg.Text("Cooling Plotter GUI")],
    [sg.Button("Ugentlig akkumuleret elforbrug", key="-CUMSUM-")],
    [sg.Button(f"Temperatur(Simple)", key="-TEMP_SIMPLE-")],
    [sg.Button("Temperatur(Smart)", key="-TEMP_SMART-")],
    [sg.Button("Histogram", key="-HISTOGRAM-")],
    [sg.Canvas(key="-CANVAS-")],
]

# Create the window
window = sg.Window(
    "Cooling Plotter Example",
    layout=layout,
    finalize=True,
    element_justification="center"
)

# Variable to track the currently displayed figure
fig_gui = None

# Main event loop
while True:
    event, values = window.read()

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
            fig = cooling_plotter.plot_weekly_temperature(duration="day", type="simple")
        elif event == "-TEMP_SMART-":
            fig = cooling_plotter.plot_weekly_temperature(duration="day", type="smart")
        elif event == "-HISTOGRAM-":
            fig = cooling_plotter.plot_histogram_cost()

        # Embed the new plot into the GUI
        fig_gui = draw_figure(window["-CANVAS-"].TKCanvas, fig)

# Close the GUI and clean up
plt.close('all')
window.close()
   
