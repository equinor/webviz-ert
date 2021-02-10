from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
from ertviz.models import (
    load_ensemble,
    ParallelCoordinatesPlotModel,
)


def parameter_comparison_controller(parent, app, suffix=""):
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
    def update_parallel_coor(_, __, selected_parameters, selected_ensembles):
        if selected_ensembles is None:
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
        parent.parallel_plot = ParallelCoordinatesPlotModel(data, colors)

        return parent.parallel_plot.repr
