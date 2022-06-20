from dash.development.base_component import Component
from webviz_config import WebvizPluginABC

from dash import html
from dash import dcc


def correlation_view(id_view: str) -> Component:
    return html.Div(
        id=f"container_{id_view}",
        className="ert-view-container",
        children=[
            dcc.Graph(
                id=id_view,
                className="ert-view-cell",
                config={"responsive": True},
            )
        ],
    )
