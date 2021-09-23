from typing import List
from dash.development.base_component import Component
from webviz_config import WebvizPluginABC

from dash import html
from dash import dcc
import dash_bootstrap_components as dbc


def response_view(parent: WebvizPluginABC, index: int = 0) -> List[Component]:
    return [
        dcc.Store(
            id={"index": index, "type": parent.uuid("response-id-store")}, data=index
        ),
        dbc.Row(
            className="ert-plot-options",
            children=[
                dbc.Col(
                    [html.H4(index)],
                    align="center",
                ),
                dbc.Col(
                    [
                        html.Label("Graph Type:", className="ert-label"),
                    ],
                    width="auto",
                    align="center",
                ),
                dbc.Col(
                    [
                        dcc.RadioItems(
                            options=[
                                {"label": key, "value": key}
                                for key in ["Function plot", "Statistics"]
                            ],
                            value="Function plot",
                            id={"index": index, "type": parent.uuid("plot-type")},
                            persistence="session",
                        ),
                    ],
                    align="center",
                ),
            ],
        ),
        dcc.Graph(
            id={
                "index": index,
                "id": parent.uuid("response-graphic"),
                "type": parent.uuid("graph"),
            },
            config={"responsive": True},
        ),
    ]
