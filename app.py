from shiny.express import ui, input
from shiny import render, reactive
from datetime import datetime
from xrds_handler import XRDS_handler
import plotly.express as px
import pandas as pd
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.transform import from_origin
from rasterio.io import MemoryFile
import tempfile
import os

import base64

import xarray as xr

from shinywidgets import render_widget

from ipyleaflet import Map, TileLayer, ImageOverlay
from localtileserver import TileClient, get_leaflet_tile_layer
import rioxarray

import matplotlib.pyplot as plt

ui.page_opts(fillable=True)

ui.input_dark_mode()

ds = XRDS_handler("./data/tg_ens_mean_0.1deg_reg_2011-2023_v29.0e.nc")
#ds = None


with ui.navset_card_pill(id="tab"):

    ### MAP FUNCTIONAL PANEL ###

    with ui.nav_panel("Climate data on Map"):
        with ui.layout_columns(col_widths=(4, 8)):
            with ui.card():
                "Functional panel"
                with ui.card():

                    ui.input_file("fileChosen_map", "Browse a file", accept=[".nc"], multiple=False)

                with ui.card():

                    if ds is not None:
                        ui.input_radio_buttons(
                            "radio_variables_map",
                            "Variables:",
                            {var:var for var in ds.get_variable_names()}
                        )
                    else:
                        "No variables"

                with ui.card():

                    ui.input_date("date_map", "Date", value='2012-01-01') 

                ### MAP OUTPUT ###

            with ui.card():
                
                @render_widget  
                def map():

                    if ds is None:
                        return Map(zoom=3.5)

                    date_str_value = input.date_map().strftime('%Y-%m-%d')
                    print(f"DDDAAATTEEE VALUE: {date_str_value}")
                    data_array = ds.get_latlon_matrix_at_given_time(input.radio_variables_map(), date_str_value)


                    if data_array.rio.crs is None:
                        data_array = data_array.rio.write_crs("EPSG:4326", inplace=True)

                    data_array.rio.set_spatial_dims(x_dim="longitude", y_dim="latitude", inplace=True)

                    cmap = plt.get_cmap("coolwarm")
                    norm = plt.Normalize(vmin=data_array.min(), vmax=data_array.max())

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

                    ui.input_file("fileChosen_graph", "Browse a file", accept=[".nc"], multiple=False)

                with ui.card():


                    if ds is not None:
                        ui.input_radio_buttons(
                            "radio_variables_graph",
                            "Variables:",
                            {var:var for var in ds.get_variable_names()}
                        )
                    else:
                        "No variables"    

                with ui.card():

                    @render.ui
                    def input_date_range():

                        if ds is not None:
                            start_date = datetime.fromtimestamp(int(ds.xrds[input.radio_variables_graph()]['time'].min().item() / 1e9)).strftime("%Y-%m-%d")
                            end_date = datetime.fromtimestamp(int(ds.xrds[input.radio_variables_graph()]['time'].max().item() / 1e9)).strftime("%Y-%m-%d")

                            return ui.input_date_range("daterange_graph", "Date range", start=start_date, end=end_date)
                        return ui.p("No file given")

                with ui.card():
                    if ds is not None:
                        "Coordinates"

                        @render.ui
                        def min_max_lat():
                            min_lat = min(ds.xrds[input.radio_variables_graph()]['latitude']).values.item()
                            max_lat = max(ds.xrds[input.radio_variables_graph()]['latitude']).values.item()

                            return ui.input_numeric("inp_lat_graph", "Latitude", 45, min=min_lat, max=max_lat)
                        
                        @render.ui
                        def min_max_lon():
                            min_lon = min(ds.xrds[input.radio_variables_graph()]['longitude']).values.item()
                            max_lon = max(ds.xrds[input.radio_variables_graph()]['longitude']).values.item()

                            return ui.input_numeric("inp_lon_graph", "Longitude", 26, min=min_lon, max=max_lon)

                    else:
                        "No file given"

            ### GRAPH OUTPUT ###

            with ui.card():

                if ds is not None:
                    @render_widget
                    def valChangeOnTime():
                        gt = ds.get_ds_at_spec_latlon(input.radio_variables_graph(), lat=input.inp_lat_graph(), lon=input.inp_lon_graph(), start=input.daterange_graph()[0], end=input.daterange_graph()[1])
                        df = gt.to_dataframe(name='value').drop(columns=['longitude', 'latitude'])

                        df['value'] = pd.to_numeric(df['value'], downcast='float')

                        fig = px.scatter(df, x=df.index, y='value', title=f"{input.radio_variables_graph()} change over time at Lat: {input.inp_lat_graph()}, Lon: {input.inp_lon_graph()}", render_mode='webgl')
                        return fig
                else:
                    "No file given"
                