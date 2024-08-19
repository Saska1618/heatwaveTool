from shiny.express import ui, input
from shiny import render, reactive, req
from datetime import datetime
from xrds_handler import XRDS_handler
import plotly.express as px
import pandas as pd
import numpy as np
import rasterio

#from rasterio.transform import from_origin
#import tempfile
import os
from shinywidgets import render_widget

from ipyleaflet import Map
from localtileserver import TileClient, get_leaflet_tile_layer

import matplotlib.pyplot as plt

ui.page_opts(fillable=True)

ui.input_dark_mode()

@reactive.calc
def get_ds():
    print("vagyok")
    ds = req(input.fileChosen())
    return XRDS_handler('./data/' + ds[0]['name'])

with ui.navset_card_pill(id="tab"):

    ### MAP FUNCTIONAL PANEL ###

    with ui.nav_panel("Upload a file"):

        with ui.card():
                    
            "Possible description"

            ui.input_file("fileChosen", "Browse a file", accept=[".nc"], multiple=False)
                    

    with ui.nav_panel("Climate data on Map"):
        with ui.layout_columns(col_widths=(4, 8)):
            with ui.card():
                "Functional panel"
                
                with ui.card():

                    @render.ui
                    def radvars_map():
                        return ui.input_radio_buttons(
                                "radio_variables_map",
                                "Variables:",
                                {var:var for var in get_ds().get_variable_names()}
                            )

                with ui.card():
                    ui.input_date("date_map", "Date", value='2012-01-01') 

                ### MAP OUTPUT ###

            with ui.card():
                
                @render_widget  
                # @reactive.event(input.fileChosen_map)
                def map():

                    date_str_value = input.date_map().strftime('%Y-%m-%d')
                    data_array = get_ds().get_latlon_matrix_at_given_time(input.radio_variables_map(), date_str_value)


                    if data_array.rio.crs is None:
                        data_array = data_array.rio.write_crs("EPSG:4326", inplace=True)

                    data_array.rio.set_spatial_dims(x_dim="longitude", y_dim="latitude", inplace=True)

                    cmap = plt.get_cmap("coolwarm")
                    norm = plt.Normalize(vmin=data_array.min().item(), vmax=data_array.max().item())
                    #norm = plt.Normalize(vmin=-22, vmax=39)

                    rgba_array =cmap(norm(data_array))
                    rgba_array = (rgba_array * 255).astype(np.uint8)


                    rgba_array[..., 3] = 128

                    nan_mask = np.isnan(data_array)
                    rgba_array[nan_mask] = [0,0,0,0]

                    if not os.path.exists(f"./tifs/colored_temperature_map_{date_str_value}.tif"):
                        with rasterio.open(f"./tifs/colored_temperature_map_{date_str_value}.tif", "w", driver="GTiff",
                                        height=rgba_array.shape[0], width=rgba_array.shape[1],
                                        count=4, dtype='uint8', crs='EPSG:4326',
                                        transform=data_array.rio.transform()) as dst:
                            dst.write(rgba_array[..., 0], 1)  # Red
                            dst.write(rgba_array[..., 1], 2)  # Green
                            dst.write(rgba_array[..., 2], 3)  # Blue
                            dst.write(rgba_array[..., 3], 4)  # Alpha

                    client = TileClient(f"./tifs/colored_temperature_map_{date_str_value}.tif")

                    tile_layer = get_leaflet_tile_layer(client)

                    center = [data_array.latitude.mean().item(), data_array.longitude.mean().item()]
                    m = Map(center=center, zoom=3.5)

                    m.add_layer(tile_layer)

                    return m

    ### OTHER TAB ###
    with ui.nav_panel("Climate data at specific location"):
        with ui.layout_columns(col_widths=(4, 8)):

            ### SETTINGS PANEL ###
            with ui.card():
                "Functional panel"
                
                with ui.card():


                    @render.ui
                    def radvars_graph():
                        return ui.input_radio_buttons(
                                "radio_variables_graph",
                                "Variables:",
                                {var:var for var in get_ds().get_variable_names()}
                            )
 

                with ui.card():

                    @render.ui
                    def input_date_range():
                        start_date = datetime.fromtimestamp(int(get_ds().xrds[input.radio_variables_graph()]['time'].min().item() / 1e9)).strftime("%Y-%m-%d")
                        end_date = datetime.fromtimestamp(int(get_ds().xrds[input.radio_variables_graph()]['time'].max().item() / 1e9)).strftime("%Y-%m-%d")

                        return ui.input_date_range("daterange_graph", "Date range", start=start_date, end=end_date)

                with ui.card():
                    "Coordinates"

                    @render.ui
                    def min_max_lat():
                        min_lat = min(get_ds().xrds[input.radio_variables_graph()]['latitude']).values.item()
                        max_lat = max(get_ds().xrds[input.radio_variables_graph()]['latitude']).values.item()

                        return ui.input_numeric("inp_lat_graph", "Latitude", 45, min=min_lat, max=max_lat)
                    
                    @render.ui
                    def min_max_lon():
                        min_lon = min(get_ds().xrds[input.radio_variables_graph()]['longitude']).values.item()
                        max_lon = max(get_ds().xrds[input.radio_variables_graph()]['longitude']).values.item()

                        return ui.input_numeric("inp_lon_graph", "Longitude", 26, min=min_lon, max=max_lon)


            ### GRAPH OUTPUT ###

            with ui.card():
                @render_widget
                def valChangeOnTime():
                    gt = get_ds().get_ds_at_spec_latlon(input.radio_variables_graph(), lat=input.inp_lat_graph(), lon=input.inp_lon_graph(), start=input.daterange_graph()[0], end=input.daterange_graph()[1])
                    df = gt.to_dataframe(name='value').drop(columns=['longitude', 'latitude'])

                    df['value'] = pd.to_numeric(df['value'], downcast='float')

                    fig = px.scatter(df, x=df.index, y='value', title=f"{input.radio_variables_graph()} change over time at Lat: {input.inp_lat_graph()}, Lon: {input.inp_lon_graph()}", render_mode='webgl')
                    return fig
                