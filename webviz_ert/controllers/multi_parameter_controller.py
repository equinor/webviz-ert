import dash
from typing import List, Tuple, Any, Optional, Mapping, Dict
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State, MATCH
import plotly.graph_objects as go
from webviz_ert.models import MultiHistogramPlotModel, load_ensemble
from webviz_ert.plugins._webviz_ert import WebvizErtPluginABC


def multi_parameter_controller(parent: WebvizErtPluginABC, app: dash.Dash) -> None:
    @app.callback(
        Output({"index": MATCH, "type": parent.uuid("bincount-store")}, "data"),
        [Input({"index": MATCH, "type": parent.uuid("hist-bincount")}, "value")],
        [State({"index": MATCH, "type": parent.uuid("bincount-store")}, "data")],
    )
    def update_bincount(hist_bincount: int, store_bincount: int) -> int:
        if not isinstance(hist_bincount, int):
            raise PreventUpdate
        if hist_bincount < 2:
            raise PreventUpdate
        if hist_bincount == store_bincount:
            raise PreventUpdate
        return hist_bincount

    @app.callback(
        [
            Output(
                {
                    "index": MATCH,
                    "id": parent.uuid("parameter-scatter"),
                    "type": parent.uuid("graph"),
                },
                "figure",
            ),
            Output({"index": MATCH, "type": parent.uuid("hist-bincount")}, "value"),
        ],
        [
            Input({"index": MATCH, "type": parent.uuid("hist-check")}, "value"),
            Input(
                {"index": MATCH, "type": parent.uuid("bincount-store")},
                "modified_timestamp",
            ),
            Input(parent.uuid("ensemble-selection-store"), "modified_timestamp"),
            Input(parent.uuid("param-label-check"), "value"),
        ],
        [
            State(parent.uuid("ensemble-selection-store"), "data"),
            State({"index": MATCH, "type": parent.uuid("parameter-id-store")}, "data"),
            State({"index": MATCH, "type": parent.uuid("bincount-store")}, "data"),
        ],
    )
    def update_histogram(
        hist_check_values: List[str],
        _: Any,
        __: Any,
        legend: List[str],
        selected_ensembles: Optional[Mapping[str, Dict]],
        parameter: str,
        bin_count: int,
    ) -> Tuple[go.Figure, int]:
        if not selected_ensembles:
            raise PreventUpdate

        data = {}
        colors = {}
        names = {}
        priors = {}
        for ensemble_id, color in selected_ensembles.items():
            ensemble = load_ensemble(parent, ensemble_id)
            if ensemble.parameters and parameter in ensemble.parameters:
                key = str(ensemble)
                parameter_model = ensemble.parameters[parameter]
                data[key] = parameter_model.data_df()
                colors[key] = color["color"]
                names[key] = key if "label" in legend else ""

                if parameter_model.priors and "prior" in hist_check_values:
                    priors[names[key]] = (parameter_model.priors, colors[key])

        parameter_plot = MultiHistogramPlotModel(
            data,
            names=names,
            colors=colors,
            hist="hist" in hist_check_values,
            kde="kde" in hist_check_values,
            priors=priors,
            bin_count=bin_count,
        )
        return parameter_plot.repr, parameter_plot.bin_count

    @app.callback(
        Output({"index": MATCH, "type": parent.uuid("hist-check")}, "options"),
        [
            Input({"index": MATCH, "type": parent.uuid("parameter-id-store")}, "data"),
        ],
        [
            State({"index": MATCH, "type": parent.uuid("hist-check")}, "options"),
            State(parent.uuid("ensemble-selection-store"), "data"),
        ],
    )
    def set_parameter_from_btn(
        parameter: str,
        plotting_options: List[Mapping[str, str]],
        selected_ensembles: Optional[Mapping[str, Dict]],
    ) -> List[Mapping[str, str]]:
        if not selected_ensembles:
            raise PreventUpdate
        has_priors = False
        for ensemble_id, _ in selected_ensembles.items():
            ensemble = load_ensemble(parent, ensemble_id)
            if ensemble.parameters and parameter in ensemble.parameters:
                parameter_model = ensemble.parameters[parameter]
                if parameter_model.priors:
                    has_priors = True
                    break
        prior_option = {"label": "prior", "value": "prior"}
        if has_priors and prior_option not in plotting_options:
            plotting_options.append(prior_option)
        if not has_priors and prior_option in plotting_options:
            plotting_options.remove(prior_option)
        return plotting_options
