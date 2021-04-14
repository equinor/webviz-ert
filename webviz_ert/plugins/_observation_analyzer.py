import dash
from dash.development.base_component import Component
import dash_html_components as html
from webviz_config import WebvizPluginABC
from typing import Mapping

# from webviz_ert.models import EnsembleModel, ParametersModel
import webviz_ert.models

from webviz_ert.views import ensemble_selector_view, response_obs_view

from webviz_ert.plugins._webviz_ert import WebvizErtPluginABC
import webviz_ert.controllers


class ObservationAnalyzer(WebvizErtPluginABC):
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
                    id=self.uuid("plotting-content"),
                    children=response_obs_view(parent=self),
                ),
            ]
        )

    def set_callbacks(self, app: dash.Dash) -> None:
        webviz_ert.controllers.ensemble_selector_controller(self, app)
        webviz_ert.controllers.observation_response_controller(self, app)
