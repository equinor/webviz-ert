import dash_html_components as html
from webviz_config import WebvizPluginABC
from ertviz.views import ensemble_selector_view, response_obs_view
from ertviz.controllers import (
    ensemble_selector_controller,
    observation_response_controller,
)


class ObservationAnalyzer(WebvizPluginABC):
    def __init__(self, app, project_identifier: str):
        super().__init__()
        self.project_identifier = project_identifier
        self.ensembles = {}
        self.parameter_models = {}
        self.set_callbacks(app)

    @property
    def layout(self):
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

    def set_callbacks(self, app):
        ensemble_selector_controller(self, app)
        observation_response_controller(self, app)
