from typing import List
from dash.development.base_component import Component
from webviz_config import WebvizPluginABC

from dash import html
from dash import dcc
import webviz_core_components as wcc
import webviz_ert.assets as assets


def ensemble_selector_list(parent: WebvizPluginABC) -> List[Component]:
    return [
        html.Div(
            [
                html.Label("Ensembles", className="ert-label"),
                wcc.Select(
                    id=parent.uuid("ensemble-multi-selector"),
                    multi=True,
                    size=10,
                    persistence=True,
                    persistence_type="session",
                    options=[],
                    value=[],
                ),
            ],
            id=parent.uuid("ensemble-multi-selector-container"),
        ),
        dcc.Dropdown(
            id=parent.uuid("selected-ensemble-dropdown"),
            value=[],
            multi=True,
            options=[],
            persistence=True,
            persistence_type="session",
        ),
        dcc.Store(id=parent.uuid("ensemble-selection-store"), storage_type="session"),
    ]
