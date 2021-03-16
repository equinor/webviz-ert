import dash
from dash.development.base_component import Component
import dash_html_components as html

import ertviz.models

from ertviz.views import (
    ensemble_selector_view,
    parallel_coordinates_view,
    parameter_selector_view,
)

import ertviz.controllers
from ertviz.plugins._webviz_ert import WebvizErtPluginABC


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
                    children=ensemble_selector_view(parent=self),
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
        ertviz.controllers.ensemble_selector_controller(self, app)
        ertviz.controllers.parameter_comparison_controller(self, app, suffix="params")
        ertviz.controllers.parameter_selector_controller(
            self, app, suffix="params", union_keys=False
        )
