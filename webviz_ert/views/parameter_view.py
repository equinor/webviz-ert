from typing import List
from typing import List
from dash.development.base_component import Component
from webviz_config import WebvizPluginABC

import dash
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
import webviz_ert.assets as assets


def parameter_view(parent: WebvizPluginABC, index: int = 0) -> List[Component]:
    return [
        dcc.Store(
            id={"index": index, "type": parent.uuid("parameter-id-store")}, data=index
        ),
        dbc.Row(
            className="ert-plot-options",
            children=[
                dbc.Col(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [html.H4(index)],
                                    align="center",
                                ),
                                dbc.Col(
                                    [
                                        html.Label("Plots:"),
                                    ],
                                    width="auto",
                                    align="center",
                                ),
                                dbc.Col(
                                    [
                                        dcc.Checklist(
                                            id={
                                                "index": index,
                                                "type": parent.uuid("hist-check"),
                                            },
                                            options=[
                                                {"label": "histogram", "value": "hist"},
                                                {"label": "kde", "value": "kde"},
                                            ],
                                            value=["hist", "kde"],
                                            persistence="session",
                                        ),
                                    ],
                                    align="center",
                                ),
                            ]
                        )
                    ],
                    width="auto",
                ),
                dbc.Col(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.Label(
                                            "Number of bins:", className="ert-label"
                                        ),
                                    ],
                                    width="auto",
                                ),
                                dbc.Col(
                                    [
                                        dcc.Input(
                                            id={
                                                "index": index,
                                                "type": parent.uuid("hist-bincount"),
                                            },
                                            type="number",
                                            placeholder="# bins",
                                            min=2,
                                            debounce=True,
                                        ),
                                    ]
                                ),
                            ]
                        )
                    ]
                ),
                dcc.Store(
                    id={"index": index, "type": parent.uuid("bincount-store")},
                    storage_type="session",
                ),
            ],
        ),
        dcc.Graph(
            id={
                "index": index,
                "id": parent.uuid("parameter-scatter"),
                "type": parent.uuid("graph"),
            },
            config={"responsive": True},
            style={"height": "450px"},
        ),
    ]
