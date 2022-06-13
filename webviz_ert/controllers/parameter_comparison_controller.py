import dash
import plotly.graph_objects as go
from typing import Any, List, Optional, Dict, Tuple

from dash.dependencies import Input, Output, State
from webviz_ert.models import (
    load_ensemble,
    ParallelCoordinatesPlotModel,
)
from webviz_ert.plugins import WebvizErtPluginABC
from webviz_ert import assets


def parameter_comparison_controller(
    parent: WebvizErtPluginABC, app: dash.Dash, suffix: str = ""
) -> None:
    graph_id = {"id": parent.uuid("parallel-coor"), "type": parent.uuid("graph")}

    @app.callback(
        [Output(graph_id, "figure"), Output(graph_id, "style")],
        [
            Input(
                parent.uuid("parameter-selection-store-" + suffix), "modified_timestamp"
            ),
            Input(parent.uuid("ensemble-selection-store"), "modified_timestamp"),
        ],
        [
            State(parent.uuid("parameter-selection-store-" + suffix), "data"),
            State(parent.uuid("ensemble-selection-store"), "data"),
        ],
    )
    def update_parallel_coor(
        _: Any,
        __: Any,
        selected_parameters: Optional[List[str]],
        selected_ensembles: Optional[Dict[str, List]],
    ) -> Tuple[go.Figure, Optional[Dict[str, str]]]:
        ensembles = None
        if selected_ensembles and selected_ensembles["selected"]:
            ensembles = selected_ensembles["selected"]

        # If no ensemble or parameter is selected just don't display the figure
        if not ensembles or not selected_parameters:
            return go.Figure(), {"display": "none"}

        data = {}
        colors = {}
        for idx, selected_ensemble in enumerate(ensembles):
            ensemble = load_ensemble(parent, selected_ensemble["value"])
            ens_key = ensemble.name
            df = ensemble.parameters_df(selected_parameters)
            df["ensemble_id"] = idx
            data[ens_key] = df.copy()
            colors[ens_key] = assets.get_color(index=idx)
        parallel_plot = ParallelCoordinatesPlotModel(data, colors)

        return parallel_plot.repr, None
