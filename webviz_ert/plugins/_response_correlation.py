import dash
import webviz_ert.assets as assets
import webviz_ert.models
import webviz_ert.controllers
import dash_bootstrap_components as dbc
from dash.development.base_component import Component
from typing import List, Dict
from webviz_ert.views import (
    ensemble_selector_list,
    correlation_view,
    parameter_selector_view,
)
from webviz_ert.models.data_model import DataType
from webviz_ert.plugins import WebvizErtPluginABC


class ResponseCorrelation(WebvizErtPluginABC):
    def __init__(self, app: dash.Dash, project_identifier: str, beta: bool = False):
        super().__init__(app, project_identifier)
        self.set_callbacks(app)
        self.beta = beta

    @property
    def tour_steps(self) -> List[Dict[str, str]]:
        steps = [
            {
                "id": self.uuid("correlation-metric"),
                "content": (
                    "Which metric to use, all views are automatically updated. "
                ),
            },
            {
                "id": self.uuid("response-overview"),
                "content": (
                    "Visualization of the currently selected response "
                    "where by clicking we can select a new index / timestep for correlation analysis."
                ),
            },
            {
                "id": self.uuid("response-scatterplot"),
                "content": (
                    "Scatterplot visualization of function values between currently selected "
                    "response and currently selected parameter. "
                    "It is accompanied by distribution plots for both selections. "
                ),
            },
            {
                "id": self.uuid("response-heatmap"),
                "content": (
                    "Heatmap based representation of correlation (-1, 1) among all selected responses "
                    "and parameters, for currently active ensembles in column-wise fashion."
                    "One can select a currently active response and parameter "
                    "by clicking directly on a heatmap. "
                ),
            },
            {
                "id": self.uuid("response-correlation"),
                "content": (
                    "Correlation BarChart for the single selected response (from heatmap) "
                    "and parameters in a descending order. "
                ),
            },
            {
                "id": self.uuid("response-info-text"),
                "content": (
                    "All responses with selected their x_index / timestep; "
                    "the currently active response and parameter are made bold. "
                ),
            },
        ]

        return steps

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
                dash.dcc.Store(
                    id=self.uuid("correlation-store-xindex"),
                    data={},
                ),
                dash.dcc.Store(
                    id=self.uuid("correlation-store-selection"),
                    data=self.load_state(
                        "active_correlation",
                        {"parameter": None, "response": None},
                    ),
                    storage_type="session",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            id=self.uuid("ensemble-content"),
                            children=ensemble_selector_list(parent=self),
                            width=4,
                        ),
                        dbc.Col(
                            [
                                parameter_selector_view(
                                    self,
                                    data_type=DataType.RESPONSE,
                                    titleLabel="Responses",
                                ),
                            ],
                            width=4,
                        ),
                        dbc.Col(
                            [
                                parameter_selector_view(
                                    self,
                                    data_type=DataType.PARAMETER,
                                    titleLabel="Parameters",
                                ),
                            ],
                            width=4,
                        ),
                    ],
                ),
                dash.dcc.RadioItems(
                    id=self.uuid("correlation-metric"),
                    options=[
                        {"label": "spearman", "value": "spearman"},
                        {"label": "pearson", "value": "pearson"},
                    ],
                    value="pearson",
                    labelStyle={"display": "inline-block"},
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            correlation_view(
                                id_view=self.uuid("response-overview"),
                            ),
                            width=3,
                            style=assets.ERTSTYLE["dbc-column"],
                        ),
                        dbc.Col(
                            correlation_view(
                                id_view=self.uuid("response-scatterplot"),
                            ),
                            width=3,
                            style=assets.ERTSTYLE["dbc-column"],
                        ),
                        dbc.Col(
                            correlation_view(
                                id_view=self.uuid("response-correlation"),
                            ),
                            width=3,
                            style=assets.ERTSTYLE["dbc-column"],
                        ),
                        dbc.Col(
                            correlation_view(
                                id_view=self.uuid("response-heatmap"),
                            ),
                            width=3,
                            style=assets.ERTSTYLE["dbc-column"],
                        ),
                    ]
                ),
                dash.html.Div(
                    id=self.uuid("response-info-text"),
                    className="ert-label",
                    children=[dash.dcc.Markdown("INFO")],
                ),
            ]
        )

    def set_callbacks(self, app: dash.Dash) -> None:
        webviz_ert.controllers.ensemble_list_selector_controller(self, app)
        webviz_ert.controllers.parameter_selector_controller(
            self, app, data_type=DataType.PARAMETER, union_keys=False
        )
        webviz_ert.controllers.parameter_selector_controller(
            self, app, data_type=DataType.RESPONSE
        )
        webviz_ert.controllers.response_correlation_controller(self, app)
