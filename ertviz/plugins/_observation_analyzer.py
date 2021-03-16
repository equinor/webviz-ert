import dash
from dash.development.base_component import Component
import dash_html_components as html
from webviz_config import WebvizPluginABC
from typing import Mapping

# from ertviz.models import EnsembleModel, ParametersModel
import ertviz.models

from ertviz.views import ensemble_selector_view, response_obs_view

from ertviz.plugins._webviz_ert import WebvizErtPluginABC
import ertviz.controllers


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
        ertviz.controllers.ensemble_selector_controller(self, app)
        ertviz.controllers.observation_response_controller(self, app)
