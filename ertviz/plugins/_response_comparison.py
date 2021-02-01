import dash_html_components as html

from webviz_config import WebvizPluginABC
from ertviz.views import ensemble_selector_view, plot_view_body, plot_view_header
from ertviz.controllers import (
    ensemble_selector_controller,
    plot_view_controller,
)


class ResponseComparison(WebvizPluginABC):
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
                    children=plot_view_header(parent=self),
                ),
                html.Div(
                    children=plot_view_body(parent=self),
                ),
            ]
        )

    def set_callbacks(self, app):
        ensemble_selector_controller(self, app)
        plot_view_controller(self, app)
