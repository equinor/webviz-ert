from typing import List
from dash.development.base_component import Component
from webviz_ert.plugins import WebvizErtPluginABC

from dash import html
from dash import dcc
import webviz_core_components as wcc
import dash_bootstrap_components as dbc


def selector_buttons(parent: WebvizErtPluginABC) -> List[Component]:
    return [
        html.Div(
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Button(
                                id=parent.uuid(f"ensemble-refresh-button"),
                                children="Refresh",
                                n_clicks=0,
                            ),
                            html.Button(
                                id=parent.uuid(f"parameter-selector-button"),
                                children=("Hide Selectors"),
                            ),
                        ]
                    ),
                ],
            )
        )
    ]


def ensemble_selector_list(parent: WebvizErtPluginABC) -> List[Component]:
    return [
        html.Div(
            dbc.Row(
                [
                    dbc.Col(
                        html.H6("Ensembles", className="ert-label"),
                        align="left",
                        width="auto",
                    ),
                ],
                align="center",
            )
        ),
        html.Div(
            wcc.Select(
                id=parent.uuid("ensemble-multi-selector"),
                multi=True,
                size=10,
                persistence=True,
                persistence_type="session",
                options=[],
                value=[],
            ),
            id=parent.uuid("container-ensemble-selector-multi"),
            className="ert-ensemble-selector-container-show",
        ),
        dcc.Dropdown(
            id=parent.uuid("selected-ensemble-dropdown"),
            value=[],
            multi=True,
            options=[],
            persistence=True,
            searchable=False,
            placeholder="",
            persistence_type="session",
            className="selected-ensemble-dropdown",
        ),
        dcc.Store(
            id=parent.uuid("ensemble-selection-store"),
            storage_type="session",
        ),
    ]
