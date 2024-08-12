from shiny.express import ui, input
from shiny import render
from datetime import datetime

ui.page_opts(fillable=True)

ui.input_dark_mode()

with ui.layout_columns(col_widths=(4, 8)):
    with ui.card():
        "Card 1"
        with ui.card():
            "Browse file"
        with ui.card():
            "Variables"
        with ui.card():
            "Lat - Lon"
            ui.input_slider("slider", "Slider", datetime.strptime("2011-01-02", '%Y-%m-%d').date(), datetime.strptime("2024-01-01", '%Y-%m-%d').date(), datetime.strptime("2012-01-01", '%Y-%m-%d').date())

    with ui.card():
        "Card 2"

        with ui.card():
            "Map"
        with ui.card():
            "Data series"
            @render.text
            def value():
                return f"{input.slider()}"