from webviz_config import WebvizPluginABC
from dash.development.base_component import Component

from dash import html
from dash import dcc
import webviz_ert.assets as assets


def parallel_coordinates_view(parent: WebvizPluginABC) -> Component:
    return html.Div(
        className="ert-view-container",
        children=[
            dcc.Graph(
                id={
                    "id": parent.uuid("parallel-coor"),
                    "type": parent.uuid("graph"),
                },
                className="ert-view-cell allow-overflow",
                config={"responsive": True},
            )
        ],
    )
