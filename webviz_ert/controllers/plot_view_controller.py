import dash
import dash_bootstrap_components as dbc

from dash import html
from typing import List, Union, Any, Dict, Tuple, Optional, Mapping
from dash.development.base_component import Component
from dash.dependencies import Input, Output, State

import webviz_ert.controllers
import webviz_ert.assets as assets

from webviz_ert.views import response_view, parameter_view
from webviz_ert.plugins import WebvizErtPluginABC
from webviz_ert.models import DataType


def _new_child(parent: WebvizErtPluginABC, plot: str, data_type: DataType) -> Component:
    if data_type == DataType.RESPONSE:
        p = response_view(parent=parent, index=plot)
    if data_type == DataType.PARAMETER:
        p = parameter_view(parent=parent, index=plot)

    return dbc.Col(
        html.Div(id=parent.uuid(plot), children=p),
        xl=12,
        lg=6,
        style=assets.ERTSTYLE["dbc-column-extra-high"],
        key=plot,
    )


def plot_view_controller(
    parent: WebvizErtPluginABC, app: dash.Dash, data_type: DataType
) -> None:
    if data_type == DataType.PARAMETER:
        webviz_ert.controllers.multi_parameter_controller(parent, app)
    elif data_type == DataType.RESPONSE:
        webviz_ert.controllers.multi_response_controller(parent, app)
    else:
        raise Exception(f"Unexpected data type `{data_type}`")

    @app.callback(
        Output(parent.uuid(f"plot-selection-store-{data_type}"), "data"),
        [
            Input(
                parent.uuid(f"parameter-selection-store-{data_type}"),
                "modified_timestamp",
            ),
        ],
        [
            State(parent.uuid(f"parameter-selection-store-{data_type}"), "data"),
            State(parent.uuid(f"plot-selection-store-{data_type}"), "data"),
        ],
    )
    def update_plot_selection(
        _: Any,
        selection: Optional[List[str]],
        current_plots: Optional[List[str]],
    ) -> List[str]:
        selection = [] if not selection else selection
        current_plots = [] if not current_plots else current_plots
        for plot in current_plots.copy():
            if plot not in selection:
                current_plots.remove(plot)
        for selected in selection:
            if selected not in current_plots:
                current_plots.append(selected)

        return current_plots

    @app.callback(
        Output(parent.uuid(f"plotting-content-{data_type}"), "children"),
        Input(parent.uuid(f"plot-selection-store-{data_type}"), "data"),
        State(parent.uuid(f"plotting-content-{data_type}"), "children"),
    )
    def create_grid(
        plots: List[str],
        bootstrap_col_children: Union[None, Component, List[Component]],
    ) -> List[Component]:
        if not plots:
            return []

        children: List[Component] = (
            [] if bootstrap_col_children is None else bootstrap_col_children
        )
        if type(children) is not list:
            children = [children]

        children_names = []
        for c in children:
            children_names.append(c["props"]["key"])

        if len(plots) > len(children_names):
            # Add new plots to the grid
            for plot in plots:
                if plot not in children_names:
                    children.append(_new_child(parent, plot, data_type))
        elif len(plots) < len(children_names):
            # Remove no longer selected plots from grid
            children = list(
                filter(lambda child: child["props"]["key"] in plots, children)
            )

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
