import dash_html_components as html
from webviz_config import WebvizPluginABC

from ertviz.views import response_view, parameter_view
from ertviz.controllers import response_controller, parameter_controller


class Ensemble(WebvizPluginABC):
    def __init__(self, app):
        super().__init__()
        self.id = "Ensemble"
        self.set_callbacks(app)

    @property
    def layout(self):
        return html.Div(
            [
                html.Div(
                    id="ensemble-content",
                    children=response_view(parent=self) + parameter_view(parent=self),
                ),
                html.Div(
                    [
                        html.Pre(id="selected-data"),
                    ]
                ),
            ]
        )

    def set_callbacks(self, app):
        response_controller(self, app)
        parameter_controller(self, app)
