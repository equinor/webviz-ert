from typing import List
from dash.development.base_component import Component
from webviz_config import WebvizPluginABC

from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from .selector_view import parameter_selector_view


def plot_view_header(parent: WebvizPluginABC) -> List[Component]:
    return [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("Responses", className="ert-label"),
                        parameter_selector_view(
                            parent, data_type="response", suffix="resp"
                        ),
                        dcc.Checklist(
                            id=parent.uuid("response-observations-check"),
                            options=[
                                {
                                    "label": "Show only responses with observations",
                                    "value": "obs",
                                },
                                {
                                    "label": "Remove all key-names ending with 'H' ( "
                                    "probably historical vectors )",
                                    "value": "historical",
                                },
                            ],
                            value=[],
                            labelStyle={"display": "block"},
                        ),
                    ],
                    width=6,
                    id=parent.uuid("response-section"),
                ),
                dbc.Col(
                    [
                        html.Label("Parameters", className="ert-label"),
                        parameter_selector_view(
                            parent, data_type="parameter", suffix="param"
                        ),
                    ],
                    width=6,
                    id=parent.uuid("parameter-section"),
                ),
            ]
        ),
        dcc.Store(id=parent.uuid("plot-selection-store"), storage_type="session"),
    ]


def plot_view_body(parent: WebvizPluginABC) -> List[Component]:
    return [
        html.Div(
            [dbc.Row(children=[], id=parent.uuid("plotting-content"))],
            id=parent.uuid("plotting-content-container"),
        ),
    ]


def plot_view_menu(parent: WebvizPluginABC) -> List[Component]:
    return [
        html.Div(
            dcc.Checklist(
                id=parent.uuid("param-label-check"),
                options=[
                    {
                        "label": "Show legend description",
                        "value": "label",
                    }
                ],
                value=["label"],
                persistence="session",
            ),
            className="ert-parameter-label-checkbox",
        ),
    ]
