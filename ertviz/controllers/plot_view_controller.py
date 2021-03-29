import dash
from webviz_config import WebvizPluginABC
from typing import List, Union, Any, Dict, Tuple, Optional, Mapping
from dash.development.base_component import Component
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_html_components as html
from ertviz.views import response_view, parameter_view
import ertviz.controllers
from ertviz.plugins._webviz_ert import WebvizErtPluginABC
import ertviz.assets as assets


def _get_child(response: str, children: List[Component]) -> Optional[Component]:
    for child in children:
        if child["props"]["children"][0]["props"]["data"] == response:
            return child
    return None


def plot_view_controller(parent: WebvizErtPluginABC, app: dash.Dash) -> None:
    ertviz.controllers.multi_response_controller(parent, app)
    ertviz.controllers.multi_parameter_controller(parent, app)

    @app.callback(
        Output(parent.uuid("plot-selection-store"), "data"),
        [
            Input(parent.uuid("parameter-selection-store-param"), "modified_timestamp"),
            Input(parent.uuid("parameter-selection-store-resp"), "modified_timestamp"),
        ],
        [
            State(parent.uuid("parameter-selection-store-param"), "data"),
            State(parent.uuid("parameter-selection-store-resp"), "data"),
            State(parent.uuid("plot-selection-store"), "data"),
        ],
    )
    def update_plot_selection(
        _: Any,
        __: Any,
        parameters: Optional[List[str]],
        responses: Optional[List[str]],
        current_selection: Optional[List[Mapping[str, str]]],
    ) -> List[Mapping[str, str]]:
        parameters = [] if not parameters else parameters
        responses = [] if not responses else responses
        current_selection = [] if not current_selection else current_selection
        for plot in current_selection.copy():
            if plot["name"] not in parameters and plot["name"] not in responses:
                current_selection.remove(plot)
        for param in parameters:
            new_plot = {"name": param, "type": "parameter"}
            if new_plot not in current_selection:
                current_selection.append(new_plot)
        for response in responses:
            new_plot = {"name": response, "type": "response"}
            if new_plot not in current_selection:
                current_selection.append(new_plot)

        return current_selection

    @app.callback(
        [
            Output(parent.uuid("plotting-content"), "children"),
            Output(parent.uuid("plotting-content-store"), "data"),
        ],
        [
            Input(parent.uuid("plot-selection-store"), "data"),
        ],
        [State(parent.uuid("plotting-content-store"), "data")],
    )
    def create_grid(
        plots: List[Dict], children: Union[None, Component, List[Component]]
    ) -> Tuple[dbc.Row, List[Component]]:
        if not plots:
            return [], []
        if children is None:
            children = []
        elif type(children) is not list:
            children = [children]
        new_children = []
        for plot in plots:
            child = _get_child(plot["name"], children)
            if child is not None:
                new_children.append(child)
            else:
                if plot["type"] == "response":
                    p = response_view(parent=parent, index=plot["name"])
                elif plot["type"] == "parameter":
                    p = parameter_view(parent=parent, index=plot["name"])
                else:
                    raise ValueError(f"Plots of undefined type {plot['type']}")
                new_children.append(html.Div(id=parent.uuid(plot["name"]), children=p))

        col_width = max(6, 12 // max(1, len(new_children)))
        bootstrapped_children = [
            dbc.Col(child, xl=col_width, lg=12, style=assets.ERTSTYLE["dbc-column"])
            for child in new_children
        ]
        return dbc.Row(bootstrapped_children), new_children
