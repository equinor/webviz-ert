import dash
import webviz_ert.controllers
import webviz_ert.models
from dash.development.base_component import Component
from typing import List, Dict
from webviz_ert.views import (
    ensemble_selector_list,
    plot_view_body,
    plot_view_header,
    plot_view_menu,
)
from webviz_ert.models.data_model import DataType
from webviz_ert.plugins import WebvizErtPluginABC


class ResponseComparison(WebvizErtPluginABC):
    def __init__(self, app: dash.Dash, project_identifier: str, beta: bool = False):
        super().__init__(app, project_identifier)
        self.set_callbacks(app)
        self.beta = beta

    @property
    def layout(self) -> Component:
        return dash.html.Div(
            [
                dash.html.Div(
                    children=[
                        dash.html.P(
                            [
                                "This page is considered a ",
                                dash.html.B("beta"),
                                " version and could be changed or removed. You are encouraged to use it and give feedback to us regarding functionality and / or bugs.",
                            ],
                            className="ert-beta-warning",
                            id=self.uuid("beta-warning"),
                        )
                    ],
                    hidden=not self.beta,
                ),
                dash.html.Div(
                    children=plot_view_header(parent=self),
                ),
                dash.html.Div(
                    children=plot_view_body(parent=self),
                ),
                dash.html.Div(
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
        webviz_ert.controllers.parameter_selector_controller(
            self, app, data_type=DataType.PARAMETER
        )
        webviz_ert.controllers.parameter_selector_controller(
            self, app, data_type=DataType.RESPONSE, extra_input=True
        )
        webviz_ert.controllers.plot_view_controller(
            self, app, webviz_ert.models.DataType.RESPONSE
        )
        webviz_ert.controllers.plot_view_controller(
            self, app, webviz_ert.models.DataType.PARAMETER
        )
