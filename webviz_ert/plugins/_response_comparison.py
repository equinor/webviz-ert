import dash
from dash.development.base_component import Component

import webviz_ert.models
from dash import html

from webviz_ert.views import (
    ensemble_selector_view,
    plot_view_body,
    plot_view_header,
    plot_view_menu,
)

import webviz_ert.controllers
from webviz_ert.plugins._webviz_ert import WebvizErtPluginABC


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
        webviz_ert.controllers.ensemble_selector_controller(self, app)
        webviz_ert.controllers.parameter_selector_controller(self, app, suffix="param")
        webviz_ert.controllers.parameter_selector_controller(
            self, app, suffix="resp", extra_input=True
        )
        webviz_ert.controllers.plot_view_controller(self, app)
