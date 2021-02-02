from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
from ertviz.models import (
    load_ensemble,
    ParallelCoordinates,
)


def parameter_comparison_controller(parent, app):
    @app.callback(
        Output(
            {"id": parent.uuid("parallel-coor"), "type": parent.uuid("graph")},
            "figure",
        ),
        [
            Input(parent.uuid("parameter-selection-store"), "modified_timestamp"),
            Input(parent.uuid("ensemble-selection-store"), "modified_timestamp"),
        ],
        [
            State(parent.uuid("parameter-selection-store"), "data"),
            State(parent.uuid("ensemble-selection-store"), "data"),
        ],
    )
    def _update_parallel_coor(
        timestamp_param, timestamp_ensemble, selected_parameters, selected_ensembles
    ):
        if None in [selected_ensembles, timestamp_param, timestamp_ensemble]:
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
        parent.parallel_plot = ParallelCoordinates(data, colors)

        return parent.parallel_plot.repr
