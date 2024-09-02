from typing import Dict, List

import dash
import dash_bootstrap_components as dbc
import dash_daq
from dash.development.base_component import Component

import webviz_ert.controllers
import webviz_ert.models
from webviz_ert import assets
from webviz_ert.models.data_model import DataType
from webviz_ert.plugins import WebvizErtPluginABC
from webviz_ert.views import (
    correlation_view,
    ensemble_selector_list,
    parameter_selector_view,
)


class ResponseCorrelation(WebvizErtPluginABC):
    def __init__(self, app: dash.Dash, project_identifier: str, beta: bool = False):
        super().__init__(app, project_identifier)
        self.set_callbacks(app)
        self.beta = beta

    @property
    def tour_steps(self) -> List[Dict[str, str]]:
        steps = [
            {
                "id": self.uuid("obs_index_selector_container"),
                "content": (
                    "Select preferred observation indexes by drawing a rectangle on the figure"
                ),
            },
            {
                "id": self.uuid("info-text"),
                "content": (
                    "The currently active response, parameter, and x_index / "
                    "timestamp"
                ),
            },
            {
                "id": self.uuid("response-overview"),
                "content": "Visualization of the currently active response",
            },
            {
                "id": self.uuid("response-scatterplot"),
                "content": (
                    "Scatterplot visualization of function values between currently active "
                    "response and currently active parameter. "
                    "It is accompanied by distribution plots for both selections. "
                ),
            },
            {
                "id": self.uuid("response-heatmap"),
                "content": (
                    "Heatmap based representation of correlation (-1, 1) among all selected responses "
                    "and parameters, for currently selected ensembles in column-wise fashion."
                    "One can select a currently active response at an observation index and parameter "
                    "by clicking directly on a heatmap. "
                ),
            },
            {
                "id": self.uuid("response-correlation"),
                "content": (
                    "Correlation BarChart for the currently active response (from heatmap) "
                    "and parameters in a descending order. "
                ),
            },
            {
                "id": self.uuid("correlation-metric"),
                "content": (
                    "Which metric to use, all views are automatically updated. "
                ),
            },
            {
                "id": self.uuid("sort-parameters"),
                "content": (
                    "Option for toggling sorting of parameters from sorting "
                    "by correlation to alphabetical; affects heatmap and "
                    "tornado plots."
                ),
            },
            {
                "id": self.uuid("hide-hover"),
                "content": (
                    "Option for toggling visibility of hover info text in " "heatmap."
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
                                " version and could be changed or removed. You are encouraged to use it and give feedback regarding functionality and / or bugs.",
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
                    storage_type="session",
                ),
                dash.dcc.Store(id=self.uuid("correlation-store-selected-obs"), data={}),
                dash.dcc.Store(
                    id=self.uuid("correlation-store-obs-range"),
                    data=self.load_state("correlation-store-obs-range", {}),
                    storage_type="session",
                ),
                dash.dcc.Store(
                    id=self.uuid("correlation-store-active-resp-param"),
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
                                dash.dcc.Checklist(
                                    id=self.uuid("response-observations-check"),
                                    options=[
                                        {
                                            "label": "Show only responses with observations",
                                            "value": "obs",
                                        },
                                    ],
                                    value=["obs"],
                                    style={"display": "none"},
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
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dash.html.Span("Observation index selector"),
                                correlation_view(
                                    id_view=self.uuid("obs_index_selector")
                                ),
                            ],
                            className="active-info",
                            style={"min-height": "10px", "padding": "20px"},
                            id=self.uuid("obs_index_selector_container"),
                        )
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            id=self.uuid("info-text"),
                            className="active-info",
                            children=[dash.html.Span("INFO")],
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            correlation_view(
                                id_view=self.uuid("response-overview"),
                            ),
                            style=assets.ERTSTYLE["dbc-column"],
                        ),
                        dbc.Col(
                            correlation_view(
                                id_view=self.uuid("response-scatterplot"),
                            ),
                            style=assets.ERTSTYLE["dbc-column"],
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            correlation_view(
                                id_view=self.uuid("response-correlation"),
                            ),
                            style=assets.ERTSTYLE["dbc-column"],
                        ),
                        dbc.Col(
                            correlation_view(
                                id_view=self.uuid("response-heatmap"),
                            ),
                            style=assets.ERTSTYLE["dbc-column"],
                        ),
                    ]
                ),
                dbc.Row(
                    children=[
                        dbc.Col(
                            dash.dcc.RadioItems(
                                id=self.uuid("correlation-metric"),
                                options=[
                                    {"label": "spearman", "value": "spearman"},
                                    {"label": "pearson", "value": "pearson"},
                                ],
                                value="pearson",
                            ),
                            className="correlation-option",
                            width="auto",
                        ),
                        dbc.Col(
                            children=[
                                dash_daq.BooleanSwitch(
                                    id=self.uuid("sort-parameters"),
                                    on=True,
                                    label="Sort parameters by correlation",
                                ),
                                dash_daq.BooleanSwitch(
                                    id=self.uuid("hide-hover"),
                                    on=False,
                                    label="Hide heatmap hover info",
                                ),
                            ],
                            className="heatmap-options",
                            width="auto",
                        ),
                    ],
                    justify="center",
                ),
            ]
        )

    def set_callbacks(self, app: dash.Dash) -> None:
        webviz_ert.controllers.ensemble_list_selector_controller(self, app)
        webviz_ert.controllers.parameter_selector_controller(
            self, app, data_type=DataType.PARAMETER, union_keys=False
        )
        webviz_ert.controllers.parameter_selector_controller(
            self, app, data_type=DataType.RESPONSE, extra_input=True
        )
        webviz_ert.controllers.response_correlation_controller(self, app)
