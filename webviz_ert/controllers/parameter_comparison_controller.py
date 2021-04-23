import dash
import plotly.graph_objects as go
from typing import Any, List, Optional, Mapping, Dict

from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
from webviz_ert.models import (
    load_ensemble,
    ParallelCoordinatesPlotModel,
)

from webviz_ert.plugins._webviz_ert import WebvizErtPluginABC


def parameter_comparison_controller(
    parent: WebvizErtPluginABC, app: dash.Dash, suffix: str = ""
) -> None:
    @app.callback(
        Output(
            {"id": parent.uuid("parallel-coor"), "type": parent.uuid("graph")},
            "figure",
        ),
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
        selected_ensembles: Optional[Mapping[str, Dict]],
    ) -> go.Figure:
        if not selected_ensembles or not selected_parameters:
            raise PreventUpdate
        selected_parameters = [] if not selected_parameters else selected_parameters

        data = {}
        colors = {}
        for idx, (ensemble_id, color) in enumerate(selected_ensembles.items()):
            ensemble = load_ensemble(parent, ensemble_id)
            ens_key = str(ensemble)
            df = ensemble.parameters_df(selected_parameters)
            df["ensemble_id"] = idx
            data[ens_key] = df.copy()
            colors[ens_key] = color["color"]
        parallel_plot = ParallelCoordinatesPlotModel(data, colors)

        return parallel_plot.repr
