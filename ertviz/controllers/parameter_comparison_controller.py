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
            Input(parent.uuid("parameter-selector-multi"), "value"),
        ],
        [State(parent.uuid("ensemble-selection-store"), "data")],
    )
    def _update_parallel_coor(parameters, selected_ensembles):
        if not selected_ensembles:
            raise PreventUpdate

        data = {}
        colors = {}

        for idx, (ensemble_id, color) in enumerate(selected_ensembles.items()):
            ensemble = load_ensemble(parent, ensemble_id)
            ens_key = str(ensemble)
            df = ensemble.parameters_df(parameters)
            df["ensemble_id"] = idx
            data[ens_key] = df.copy()
            colors[ens_key] = color["color"]
        parent.parallel_plot = ParallelCoordinates(data, colors)
        return parent.parallel_plot.repr
