from typing import List

import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.development.base_component import Component
from webviz_config import WebvizPluginABC


def parameter_view(parent: WebvizPluginABC, index: str = "") -> List[Component]:
    return [
        dcc.Store(
            id={"index": index, "type": parent.uuid("parameter-id-store")}, data=index
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    [
                        html.H4(
                            index,
                            className="ert-parameter-view-caption",
                            id={
                                "index-caption": index,
                                "type": parent.uuid("parameter-id-store"),
                            },
                        )
                    ],
                    align="left",
                ),
                dbc.Tooltip(
                    index,
                    target={
                        "index-caption": index,
                        "type": parent.uuid("parameter-id-store"),
                    },
                    placement="bottom-start",
                    class_name="ert-parameter-view-caption-tooltip",
                ),
            ]
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    [
                        html.Label("Plots:"),
                    ],
                    width="auto",
                    align="left",
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
                    align="left",
                    width="auto",
                ),
                dbc.Col(
                    [
                        html.Label("Number of bins:", className="ert-label"),
                    ],
                    align="left",
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
                            className="ert-input-number",
                        ),
                    ],
                    align="left",
                    width="auto",
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
