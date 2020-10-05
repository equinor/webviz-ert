import dash_html_components as html
from webviz_config import WebvizPluginABC

from ertviz.views import timeseries_view
from ertviz.controllers import timeseries_controller


class Ensemble(WebvizPluginABC):
    def __init__(self, app):
        super().__init__()
        self.id = "Ensemble"
        self.set_callbacks(app)

    @property
    def layout(self):
        return html.Div(id="ensemble-content", children=timeseries_view(parent=self))

    def set_callbacks(self, app):
        timeseries_controller(self, app)
