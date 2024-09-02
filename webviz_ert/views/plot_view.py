from typing import List

import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.development.base_component import Component

from webviz_ert.models.data_model import DataType
from webviz_ert.plugins import WebvizErtPluginABC

from .ensemble_selector_view import ensemble_selector_list
from .selector_view import parameter_selector_view


def plot_view_header(parent: WebvizErtPluginABC) -> List[Component]:
    return [
        dbc.Row(
            [
                dbc.Col(
                    id=parent.uuid("ensemble-content"),
                    children=ensemble_selector_list(parent=parent),
                    width=4,
                ),
                dbc.Col(
                    [
                        parameter_selector_view(
                            parent,
                            data_type=DataType.RESPONSE,
                            titleLabel="Responses",
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
                    width=4,
                    id=parent.uuid("response-section"),
                ),
                dbc.Col(
                    [
                        parameter_selector_view(
                            parent,
                            data_type=DataType.PARAMETER,
                            titleLabel="Parameters",
                        ),
                    ],
                    width=4,
                    id=parent.uuid("parameter-section"),
                ),
            ]
        ),
        dcc.Store(id=parent.uuid("plot-selection-store-resp"), storage_type="session"),
        dcc.Store(id=parent.uuid("plot-selection-store-param"), storage_type="session"),
    ]


def plot_view_body(parent: WebvizErtPluginABC) -> List[Component]:
    return [
        html.Div(
            [
                dbc.Row(children=[], id=parent.uuid("plotting-content-resp")),
                dbc.Row(children=[], id=parent.uuid("plotting-content-param")),
            ],
            id=parent.uuid("plotting-content-container"),
        ),
    ]


def plot_view_menu(parent: WebvizErtPluginABC) -> List[Component]:
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
