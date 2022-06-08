import dash
from dash.development.base_component import Component
from typing import List, Dict

import webviz_ert.models
from dash import html

from webviz_ert.views import (
    ensemble_selector_list,
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
                    children=ensemble_selector_list(parent=self),
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

    @property
    def tour_steps(self) -> List[Dict[str, str]]:
        steps = [
            {
                "id": self.uuid("ensemble-multi-selector"),
                "content": "List of experiment ensembles.",
            },
            {
                "id": self.uuid("selected-ensemble-dropdown"),
                "content": "List of currently selected ensembles.",
            },
            {
                "id": self.uuid(f"ensemble-refresh-button"),
                "content": (
                    "Forces a refresh of all ensemble data including parameter and response data."
                ),
            },
            {
                "id": self.uuid("response-section"),
                "content": "Response section.",
            },
            {
                "id": self.uuid(f"parameter-selector-multi-resp"),
                "content": (
                    "List of responses. This list is populated only"
                    " if at least one ensemble is selected."
                    " Selecting multiple responses is possible"
                    " using mouse `Click + Drag` inside the response list."
                ),
            },
            {
                "id": self.uuid(f"parameter-deactivator-resp"),
                "content": "List of currently selected responses.",
            },
            {
                "id": self.uuid(f"parameter-selector-filter-resp"),
                "content": (
                    "Response search field. The response list will show only"
                    " elements that contain the search characters"
                ),
            },
            {
                "id": self.uuid("parameter-section"),
                "content": "Parameter section",
            },
            {
                "id": self.uuid(f"parameter-selector-multi-param"),
                "content": (
                    "List of parameters. This list is populated only"
                    " if at least one ensemble is selected."
                    " Selecting multiple parameters is possible"
                    " using mouse `Click + Drag` inside the response list."
                ),
            },
            {
                "id": self.uuid(f"parameter-deactivator-param"),
                "content": "List of currently selected parameters.",
            },
            {
                "id": self.uuid(f"parameter-selector-filter-param"),
                "content": (
                    "Search field. The parameter list will show only"
                    " elements that contain the search characters"
                ),
            },
        ]
        return steps

    def set_callbacks(self, app: dash.Dash) -> None:
        webviz_ert.controllers.ensemble_list_selector_controller(self, app)
        webviz_ert.controllers.parameter_selector_controller(self, app, suffix="param")
        webviz_ert.controllers.parameter_selector_controller(
            self, app, suffix="resp", extra_input=True
        )
        webviz_ert.controllers.plot_view_controller(self, app)
