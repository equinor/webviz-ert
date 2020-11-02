import dash_html_components as html
from webviz_config import WebvizPluginABC
from ertviz.data_loader import get_ensembles
import dash_core_components as dcc
from ertviz.views import ensemble_selector_view, response_view
from ertviz.controllers import ensemble_selector_controller, multi_response_controller


class EnsembleComparison(WebvizPluginABC):
    def __init__(self, app):
        super().__init__()
        self.ensembles = {}
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
                    children=response_view(parent=self),
                ),
            ]
        )

    def set_callbacks(self, app):
        ensemble_selector_controller(self, app)
        multi_response_controller(self, app)
