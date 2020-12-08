from copy import deepcopy
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_core_components as dcc
from webviz_config import WebvizPluginABC
from ertviz.views import ensemble_selector_view, response_view, parameter_view
from ertviz.controllers import (
    ensemble_selector_controller,
    multi_response_controller,
    multi_parameter_controller,
)


class ResponseComparison(WebvizPluginABC):
    def __init__(self, app, project_identifier: str):
        super().__init__()
        self.project_identifier = project_identifier
        self.ensembles = {}
        self.parameter_models = {}
        self.set_callbacks(app)

    @property
    def layout(self):
        return html.Div(
            [
                html.Div(
                    id=self.uuid("ensemble-content"),
                    children=ensemble_selector_view(parent=self),
                ),
                html.Div(
                    className="ert-dropdown-container",
                    children=[
                        html.Label("# of Plots: ", className="ert-label"),
                        dcc.Input(
                            id=self.uuid("grid_size"),
                            type="number",
                            placeholder="Grid size..",
                            value=1,
                            className="ert-dropdown",
                        ),
                    ],
                ),
                html.Div(
                    id=self.uuid("plotting-content"),
                ),
            ]
        )

    def set_callbacks(self, app):
        ensemble_selector_controller(self, app)
        multi_response_controller(self, app)

        @app.callback(
            Output(self.uuid("plotting-content"), "children"),
            [Input(self.uuid("grid_size"), "value")],
            [State(self.uuid("plotting-content"), "children")],
        )
        def _create_grid(grid_size, children):
            if grid_size is None:
                raise PreventUpdate
            if children is None:
                children = []
            elif type(children) is not list:
                children = [children]

            new_children = []
            for i in range(grid_size):
                if i < len(children):
                    new_children.append(children[i])
                else:
                    new_children.append(
                        html.Div(
                            response_view(parent=self, index=i),
                            className="ert-graph-multi",
                        )
                    )
            return new_children
