import dash
from dash.development.base_component import Component
from typing import List, Dict

from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from webviz_ert.views import (
    ensemble_selector_list,
    correlation_view,
    parameter_selector_view,
    element_dropdown_view,
)
import webviz_ert.assets as assets
import webviz_ert.models
from webviz_ert.plugins._webviz_ert import WebvizErtPluginABC
import webviz_ert.controllers


class ResponseCorrelation(WebvizErtPluginABC):
    def __init__(self, app: dash.Dash, project_identifier: str):
        super().__init__(app, project_identifier)
        self.set_callbacks(app)

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
        return html.Div(
            [
                dcc.Store(
                    id=self.uuid("correlation-store-xindex"),
                    data={},
                ),
                dcc.Store(
                    id=self.uuid("correlation-store-selection"),
                    data={"parameter": "x", "response": "y"},
                ),
                html.Div(
                    id=self.uuid("ensemble-content"),
                    children=ensemble_selector_list(parent=self),
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Label("Responses", className="ert-label"),
                                parameter_selector_view(
                                    self, data_type="response", suffix="resp"
                                ),
                            ],
                            width=4,
                        ),
                        dbc.Col(
                            [
                                html.Label("Parameters", className="ert-label"),
                                parameter_selector_view(
                                    self, data_type="parameter", suffix="param"
                                ),
                            ],
                            width=4,
                        ),
                        dbc.Col(
                            [
                                html.Label("Parameters", className="ert-label"),
                                element_dropdown_view(
                                    self, data_type=webviz_ert.models.DataType.RESPONSE
                                ),
                            ],
                            width=4,
                        ),
                    ],
                ),
                dcc.RadioItems(
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
                                parent=self,
                                id_view=self.uuid("response-overview"),
                            ),
                            width=3,
                            style=assets.ERTSTYLE["dbc-column"],
                        ),
                        dbc.Col(
                            correlation_view(
                                parent=self,
                                id_view=self.uuid("response-scatterplot"),
                            ),
                            width=3,
                            style=assets.ERTSTYLE["dbc-column"],
                        ),
                        dbc.Col(
                            correlation_view(
                                parent=self,
                                id_view=self.uuid("response-correlation"),
                            ),
                            width=3,
                            style=assets.ERTSTYLE["dbc-column"],
                        ),
                        dbc.Col(
                            correlation_view(
                                parent=self,
                                id_view=self.uuid("response-heatmap"),
                            ),
                            width=3,
                            style=assets.ERTSTYLE["dbc-column"],
                        ),
                    ]
                ),
                html.Div(
                    id=self.uuid("response-info-text"),
                    className="ert-label",
                    children=[dcc.Markdown("INFO")],
                ),
            ]
        )

    def set_callbacks(self, app: dash.Dash) -> None:
        webviz_ert.controllers.ensemble_list_selector_controller(self, app)
        webviz_ert.controllers.parameter_selector_controller(
            self, app, suffix="param", union_keys=False
        )
        webviz_ert.controllers.parameter_selector_controller(self, app, suffix="resp")
        webviz_ert.controllers.element_dropdown_controller(
            self, app, webviz_ert.models.DataType.RESPONSE
        )
        webviz_ert.controllers.response_correlation_controller(self, app)
