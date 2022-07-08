import dash
import webviz_ert.models
import webviz_ert.controllers
from dash.development.base_component import Component
from typing import List, Dict
from webviz_ert.views import ensemble_selector_list, response_obs_view
from webviz_ert.plugins import WebvizErtPluginABC


class ObservationAnalyzer(WebvizErtPluginABC):
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
                    id=self.uuid("ensemble-content"),
                    children=ensemble_selector_list(parent=self),
                ),
                dash.html.Div(
                    id=self.uuid("plotting-content"),
                    children=response_obs_view(parent=self),
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
                "id": self.uuid("response-selector"),
                "content": (
                    "Response selection list will be populated"
                    " when an ensemble is selected in the list of ensembles"
                    " and will contain only responses that have observations."
                ),
            },
            {
                "id": self.uuid("observations-graph-container"),
                "content": (
                    "Representation of the misfit between the estimated response value from the forward model"
                    " and the existing observation values."
                    " One can choose to show misfits grouped by time (Univeriate) as candles"
                    " showing misfits statistics per a single time point"
                    " or to render misfits as a histogram aggregating misfits over the entire temporal axes (Summary)."
                    " When multiple ensembles are selected each graph will be overlayed on top of each other"
                    " transparently, where each ensemble gets its own colour"
                ),
            },
        ]
        return steps

    def set_callbacks(self, app: dash.Dash) -> None:
        webviz_ert.controllers.ensemble_list_selector_controller(self, app)
        webviz_ert.controllers.observation_response_controller(self, app)
