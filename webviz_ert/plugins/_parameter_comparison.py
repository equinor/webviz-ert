import dash
from dash.development.base_component import Component
from typing import List, Dict
from dash import html

import webviz_ert.models

from webviz_ert.views import (
    ensemble_selector_list,
    parallel_coordinates_view,
    parameter_selector_view,
)

import webviz_ert.controllers
from webviz_ert.plugins import WebvizErtPluginABC
from webviz_ert.models.data_model import DataType


class ParameterComparison(WebvizErtPluginABC):
    def __init__(self, app: dash.Dash, project_identifier: str):
        super().__init__(app, project_identifier)
        self.set_callbacks(app)

    @property
    def layout(self) -> Component:
        return html.Div(
            [
                html.Div(
                    id=self.uuid("ensemble-content"),
                    children=ensemble_selector_list(parent=self),
                ),
                html.Div(
                    id=self.uuid("parallel-coor-content"),
                    children=[
                        html.H5("Multi parameter selector:"),
                        parameter_selector_view(
                            parent=self, data_type=DataType.PARAMETER
                        ),
                        parallel_coordinates_view(parent=self),
                    ],
                ),
            ]
        )

    @property
    def tour_steps(self) -> List[Dict[str, str]]:
        steps = [
            {
                "id": self.uuid("ensemble-multi-selector"),
                "content": "List of experiment ensembles.",
            },
            {
                "id": self.uuid("selected-ensemble-dropdown"),
                "content": "List of currently selected ensembles.",
            },
            {
                "id": self.uuid(f"ensemble-refresh-button"),
                "content": (
                    "Forces a refresh of all ensemble data including parameter and response data."
                ),
            },
            {
                "id": self.uuid(f"parameter-selector-multi-param"),
                "content": (
                    "List of parameters. This list is populated only"
                    " if at least one ensemble is selected."
                    " Selecting multiple parameters is possible"
                    " using mouse `Click + Drag` inside the response list."
                ),
            },
            {
                "id": self.uuid(f"parameter-deactivator-param"),
                "content": (
                    "List of currently selected parameters."
                    "Every selected parameter is visualized in the parallel coordinates plot,"
                    " where each vertical axis represents a single parameter."
                    " Multiple ensembles are distinguished by different colors."
                ),
            },
            {
                "id": self.uuid(f"parameter-selector-filter-param"),
                "content": (
                    "Search field. The parameter list will show only"
                    " elements that contain the search characters"
                ),
            },
        ]
        return steps

    def set_callbacks(self, app: dash.Dash) -> None:
        webviz_ert.controllers.ensemble_list_selector_controller(self, app)
        webviz_ert.controllers.parameter_selector_controller(
            self, app, data_type=DataType.PARAMETER, union_keys=False
        )
        webviz_ert.controllers.parameter_comparison_controller(self, app)
