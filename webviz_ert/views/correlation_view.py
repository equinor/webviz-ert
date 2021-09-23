from dash.development.base_component import Component
from webviz_config import WebvizPluginABC

from dash import html
from dash import dcc


def correlation_view(parent: WebvizPluginABC, id_view: str) -> Component:
    return html.Div(
        id=id_view,
        className="ert-view-container",
        children=[
            dcc.Graph(
                id={
                    "id": id_view,
                    "type": parent.uuid("graph"),
                },
                className="ert-view-cell",
                config={"responsive": True},
            )
        ],
    )
