import dash
from dash.development.base_component import Component
from typing import Mapping

# from ertviz.models import EnsembleModel, ParametersModel
import ertviz.models
import dash_html_components as html

from ertviz.views import (
    ensemble_selector_view,
    plot_view_body,
    plot_view_header,
    plot_view_menu,
)

import ertviz.controllers
from ertviz.plugins._webviz_ert import WebvizErtPluginABC


class ResponseComparison(WebvizErtPluginABC):
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
                    children=plot_view_header(parent=self),
                ),
                html.Div(
                    children=plot_view_body(parent=self),
                ),
                html.Div(
                    children=plot_view_menu(parent=self),
                ),
            ]
        )

    def set_callbacks(self, app: dash.Dash) -> None:
        ertviz.controllers.ensemble_selector_controller(self, app)
        ertviz.controllers.parameter_selector_controller(self, app, suffix="param")
        ertviz.controllers.parameter_selector_controller(
            self, app, suffix="resp", extra_input=True
        )
        ertviz.controllers.plot_view_controller(self, app)
