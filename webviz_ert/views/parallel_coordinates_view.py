from dash import dcc, html
from dash.development.base_component import Component
from webviz_config import WebvizPluginABC


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
