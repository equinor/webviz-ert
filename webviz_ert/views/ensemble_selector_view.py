from typing import List
from dash.development.base_component import Component
from webviz_config import WebvizPluginABC

from dash import html
from dash import dcc
import dash_cytoscape as cyto
import webviz_ert.assets as assets


cyto.load_extra_layouts()


def ensemble_selector_view(parent: WebvizPluginABC) -> List[Component]:
    return [
        html.Div(
            [
                cyto.Cytoscape(
                    id=parent.uuid("ensemble-selector"),
                    layout={"name": "grid"},
                    className="ert-ensemble-selector-large",
                    stylesheet=assets.ERTSTYLE["ensemble-selector"]["stylesheet"],
                    responsive=False,
                ),
                html.Button(
                    id=parent.uuid("ensemble-selector-button"),
                    className="ert-ensemble-selector-view-toggle",
                    children=("Minimize"),
                ),
            ],
            id=parent.uuid("ensemble-selector-container"),
            className="ert-ensemble-selector-container-large",
        ),
        dcc.Store(id=parent.uuid("ensemble-selection-store"), storage_type="session"),
        dcc.Store(
            id=parent.uuid("ensemble-view-store"), storage_type="session", data=True
        ),
    ]
