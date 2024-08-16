from shiny.express import ui, input
from shiny import render, reactive
from datetime import datetime
from xrds_handler import XRDS_handler
import plotly.express as px
import pandas as pd

from shinywidgets import render_widget

from ipyleaflet import Map, TileLayer
from localtileserver import TileClient, get_leaflet_tile_layer
import rioxarray

import matplotlib.pyplot as plt

ui.page_opts(fillable=True)

ui.input_dark_mode()



ds = XRDS_handler("./data/tg_ens_mean_0.1deg_reg_2011-2023_v29.0e.nc")



with ui.navset_card_pill(id="tab"):

    ### MAP FUNCTIONAL PANEL ###

    with ui.nav_panel("Climate data on Map"):
        with ui.layout_columns(col_widths=(4, 8)):
            with ui.card():
                "Functional panel"
                with ui.card():

                    ui.input_file("fileChosen_map", "Browse a file", accept=[".nc"], multiple=False)

                with ui.card():

                    ui.input_radio_buttons(
                        "radio_variables_map",
                        "Variables:",
                        {var:var for var in ds.get_variable_names()}
                    )

                with ui.card():

                    ui.input_date("date_map", "Date", value='2012-01-01') 

                ### MAP OUTPUT ###

            with ui.card():

                # @render.plot
                # def plvalue():
                #     date_str_value = input.date_map().strftime('%Y-%m-%d')
                #     gs = ds.get_latlon_matrix_at_given_time(input.radio_variables_map(), date_str_value)
                #     gs.plot()
                #     plt.title(f"{input.radio_variables_map()} data on {input.date_map()}")
                #     return plt.gcf()
                
                @render_widget  
                def map():
                    # date_str_value = input.date_map().strftime('%Y-%m-%d')
                    # data_array = ds.get_latlon_matrix_at_given_time(input.radio_variables_map(), date_str_value)

                    # data_array.rio.set_spatial_dims(x_dim="longitude", y_dim="latitude", inplace=True)

                    # data_array.rio.to_raster("temperature_map.tif")

                    # client = TileClient("temperature_map.tif")

                    # tile_layer = get_leaflet_tile_layer(client)

                    # center = [data_array.latitude.mean().item(), data_array.longitude.mean().item()]
                    # m = Map(center=center, zoom=5)

                    # m.add_layer(tile_layer)

                    # return m
                    return Map(center=(50.6252978589571, 0.34580993652344), zoom=3)
        

    ### OTHER TAB ###
    with ui.nav_panel("Climate data at specific location"):
        with ui.layout_columns(col_widths=(4, 8)):

            ### SETTINGS PANEL ###
            with ui.card():
                "Functional panel"
                with ui.card():

                    ui.input_file("fileChosen_graph", "Browse a file", accept=[".nc"], multiple=False)

                with ui.card():

                    ui.input_radio_buttons(
                        "radio_variables_graph",
                        "Variables:",
                        {var:var for var in ds.get_variable_names()}
                    )

                with ui.card():

                    @render.ui
                    def input_date_range():

                        start_date = datetime.fromtimestamp(int(ds.xrds[input.radio_variables_graph()]['time'].min().item() / 1e9)).strftime("%Y-%m-%d")
                        end_date = datetime.fromtimestamp(int(ds.xrds[input.radio_variables_graph()]['time'].max().item() / 1e9)).strftime("%Y-%m-%d")

                        return ui.input_date_range("daterange_graph", "Date range", start=start_date, end=end_date)

                with ui.card():
                    "Coordinates"

                    min_lat, max_lat = ds.get_minmax_latitude()
                    min_lon, max_lon = ds.get_minmax_longitude()

                    ui.input_numeric("inp_lat_graph", "Latitude", 45, min=min_lat, max=max_lat)
                    ui.input_numeric("inp_lon_graph", "Longitude", 26, min=min_lon, max=max_lon)


            ### GRAPH OUTPUT ###

            with ui.card():
                
                @render_widget
                def valChangeOnTime():
                    gt = ds.get_ds_at_spec_latlon(input.radio_variables_graph(), lat=input.inp_lat_graph(), lon=input.inp_lon_graph(), start=input.daterange_graph()[0], end=input.daterange_graph()[1])
                    df = gt.to_dataframe(name='value').drop(columns=['longitude', 'latitude'])

                    df['value'] = pd.to_numeric(df['value'], downcast='float')

                    fig = px.scatter(df, x=df.index, y='value', title=f"{input.radio_variables_graph()} change over time at Lat: {input.inp_lat_graph()}, Lon: {input.inp_lon_graph()}", render_mode='webgl')
                    return fig
                