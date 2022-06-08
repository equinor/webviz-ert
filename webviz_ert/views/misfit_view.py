from typing import List
from dash.development.base_component import Component
from webviz_config import WebvizPluginABC

from dash import html
from dash import dcc


def response_obs_view(parent: WebvizPluginABC) -> List[Component]:
    return [
        html.H5("Observation/Misfits plots"),
        html.Div(
            className="ert-dropdown-container",
            children=[
                html.Label("Response", className="ert-label"),
                dcc.Dropdown(
                    id=parent.uuid("response-selector"),
                    className="ert-dropdown",
                ),
                dcc.Store(
                    id=parent.uuid("response-selector-store"),
                    data=None,
                    storage_type="session",
                ),
            ],
        ),
        html.Div(
            [
                html.Div(
                    className="ert-graph-options",
                    children=[
                        html.Label("Y-axis type:"),
                        dcc.RadioItems(
                            options=[
                                {"label": key, "value": key}
                                for key in ["linear", "log"]
                            ],
                            value="linear",
                            id=parent.uuid("yaxis-type"),
                        ),
                        html.Label("Misfits Type:"),
                        dcc.RadioItems(
                            options=[
                                {"label": key, "value": key}
                                for key in ["Univariate", "Summary"]
                            ],
                            value="Univariate",
                            id=parent.uuid("misfits-type"),
                        ),
                    ],
                ),
                dcc.Graph(
                    id={
                        "id": parent.uuid("response-graphic"),
                        "type": parent.uuid("graph"),
                    },
                    className="ert-graph",
                ),
            ],
            className="ert-graph-container",
            id=parent.uuid("observations-graph-container"),
        ),
    ]
