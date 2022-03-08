import dash
import dash_bootstrap_components as dbc

from dash import html
from typing import List, Union, Any, Dict, Tuple, Optional, Mapping
from dash.development.base_component import Component
from dash.dependencies import Input, Output, State

import webviz_ert.controllers
import webviz_ert.assets as assets

from webviz_ert.views import response_view, parameter_view
from webviz_ert.plugins._webviz_ert import WebvizErtPluginABC


def _new_child(parent: WebvizErtPluginABC, plot: Dict) -> Component:
    if plot["type"] == "response":
        p = response_view(parent=parent, index=plot["name"])
    elif plot["type"] == "parameter":
        p = parameter_view(parent=parent, index=plot["name"])
    else:
        raise ValueError(f"Plots of undefined type {plot['type']}")

    return dbc.Col(
        html.Div(id=parent.uuid(plot["name"]), children=p),
        xl=12,
        lg=6,
        style=assets.ERTSTYLE["dbc-column"],
        key=plot["name"],
    )


def plot_view_controller(parent: WebvizErtPluginABC, app: dash.Dash) -> None:
    webviz_ert.controllers.multi_response_controller(parent, app)
    webviz_ert.controllers.multi_parameter_controller(parent, app)

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
        Output(parent.uuid("plotting-content"), "children"),
        Input(parent.uuid("plot-selection-store"), "data"),
        State(parent.uuid("plotting-content"), "children"),
    )
    def create_grid(
        plots: List[Dict],
        boostrap_col_childeren: Union[None, Component, List[Component]],
    ) -> List[Component]:
        if not plots:
            return []

        children: List[Component] = (
            [] if boostrap_col_childeren is None else boostrap_col_childeren
        )
        if type(children) is not list:
            children = [children]

        children_names = []
        for c in children:
            children_names.append(c["props"]["key"])

        if len(plots) > len(children_names):
            # Add new plots to the grid
            for plot in plots:
                if plot["name"] not in children_names:
                    children.append(_new_child(parent, plot))
        elif len(plots) < len(children_names):
            # Remove some plot from the grid
            plot_names = [p["name"] for p in plots]
            idx = next(i for i, c in enumerate(children_names) if c not in plot_names)
            del children[idx]

        for c in children:
            xl_width = 6 if len(children) > 1 else 12
            if isinstance(c, dict):
                c["props"]["xl"] = xl_width
            else:
                c.xl = xl_width

        # Every change to the childred even if the there is no change
        # and the input is returned as output triggers a redrawing
        # of every plot in the graph grid. This will sap performance
        # for very large data sets or large number of plots in the grid.
        # There is no clear way to avoid this wihtout redesigning the grid.
        return children
