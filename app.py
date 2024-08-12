from shiny.express import ui, input
from shiny import render
from datetime import datetime
from xrds_handler import XRDS_handler

from shinywidgets import render_widget

from ipyleaflet import Map

import matplotlib.pyplot as plt

ui.page_opts(fillable=True)

ui.input_dark_mode()

ds = XRDS_handler("./data/tg_ens_mean_0.1deg_reg_2011-2023_v29.0e.nc")

with ui.layout_columns(col_widths=(4, 8)):
    with ui.card():
        "Functional panel"
        with ui.card():
            "Browse file"
            ui.input_file("fileChosen", "Choose a file", accept=[".nc"], multiple=False)
    
        with ui.card():
            "Variables:"

            ui.input_radio_buttons(
                "radio_variables",
                "",
                {var:var for var in ds.get_variable_names()}
            )

            ui.input_slider("slider", "Select a date", datetime.strptime("2011-01-02", '%Y-%m-%d').date(), datetime.strptime("2024-01-01", '%Y-%m-%d').date(), datetime.strptime("2012-01-01", '%Y-%m-%d').date())


        with ui.card():
            "Lat - Lon"

            
            
            min_lat, max_lat = ds.get_minmax_latitude()
            min_lon, max_lon = ds.get_minmax_longitude()

            ui.input_numeric("inp_lat", "Latitude", 45, min=min_lat, max=max_lat)
            ui.input_numeric("inp_lon", "Longitude", 26, min=min_lon, max=max_lon)

            @render.text
            def preValues():

                return f"Lat: {input.inp_lat()}, Lot: {input.inp_lon()}"
            
    with ui.card():
        "Output panel"

        with ui.card():
            "Map"

            # @render_widget
            # def map():
            #     return Map(center=(50.6252978589571, 0.34580993652344), zoom=3)
            
            @render.plot
            def plvalue():
                date_str_value = input.slider().strftime('%Y-%m-%d')
                gs = ds.get_latlon_matrix_at_given_time(input.radio_variables(), date_str_value)
                gs.plot()
                return plt.gcf()


        with ui.card():

            @render.text
            def value():
                return f"{input.radio_variables()} change over time at Lat: {input.inp_lat()}, Lon: {input.inp_lon()}"
            
            @render.plot
            def valChangeOnTime():
                gt = ds.get_ds_at_spec_latlon(input.radio_variables(), lat=input.inp_lat(), lon=input.inp_lon())
                gt.plot()
                return plt.gcf()
            
            