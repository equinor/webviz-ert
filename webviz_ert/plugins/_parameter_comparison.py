import dash
from dash.development.base_component import Component
from dash import html

import webviz_ert.models

from webviz_ert.views import (
    ensemble_selector_list,
    parallel_coordinates_view,
    parameter_selector_view,
)

import webviz_ert.controllers
from webviz_ert.plugins._webviz_ert import WebvizErtPluginABC


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
                            parent=self, data_type="parameter", suffix="params"
                        ),
                        parallel_coordinates_view(parent=self),
                    ],
                ),
            ]
        )

    def set_callbacks(self, app: dash.Dash) -> None:
        webviz_ert.controllers.ensemble_list_selector_controller(self, app)
        webviz_ert.controllers.parameter_selector_controller(
            self, app, suffix="params", union_keys=False
        )
        webviz_ert.controllers.parameter_comparison_controller(
            self, app, suffix="params"
        )
