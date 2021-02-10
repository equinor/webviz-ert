import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from webviz_config import WebvizPluginABC
from ertviz.views import (
    ensemble_selector_view,
    correlation_view,
    parameter_selector_view,
)
from ertviz.controllers import (
    ensemble_selector_controller,
    response_correlation_controller,
    parameter_selector_controller,
)


class ResponseCorrelation(WebvizPluginABC):
    def __init__(self, app, project_identifier: str):
        super().__init__()
        self.project_identifier = project_identifier
        self.ensembles = {}
        self.set_callbacks(app)

    @property
    def layout(self):
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
                    children=ensemble_selector_view(parent=self),
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
                            width=6,
                        ),
                        dbc.Col(
                            [
                                html.Label("Parameters", className="ert-label"),
                                parameter_selector_view(
                                    self, data_type="parameter", suffix="param"
                                ),
                            ],
                            width=6,
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
                        ),
                        dbc.Col(
                            correlation_view(
                                parent=self,
                                id_view=self.uuid("response-scatterplot"),
                            ),
                            width=3,
                        ),
                        dbc.Col(
                            correlation_view(
                                parent=self,
                                id_view=self.uuid("response-correlation"),
                            ),
                            width=3,
                        ),
                        dbc.Col(
                            correlation_view(
                                parent=self,
                                id_view=self.uuid("response-heatmap"),
                            ),
                            width=3,
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

    def set_callbacks(self, app):
        ensemble_selector_controller(self, app)
        response_correlation_controller(self, app)
        parameter_selector_controller(self, app, suffix="param", union_keys=False)
        parameter_selector_controller(self, app, suffix="resp")
