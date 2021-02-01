import dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State, MATCH
import plotly.graph_objects as go
from ertviz.models import EnsembleModel, MultiHistogramPlotModel, load_ensemble
import ertviz.assets as assets


def multi_parameter_controller(parent, app):
    @app.callback(
        [
            Output(parent.uuid("parameter-selector"), "options"),
            Output(parent.uuid("parameter-selector"), "value"),
        ],
        [
            Input(parent.uuid("ensemble-selection-store"), "data"),
            Input(parent.uuid("response-observations-check"), "value"),
        ],
        [State(parent.uuid("plot-selection-store"), "data")],
    )
    def update_parameter_options(selected_ensembles, _, prev_plot_selection):
        prev_plot_selection = [] if not prev_plot_selection else prev_plot_selection
        if not selected_ensembles:
            raise PreventUpdate
        ensemble_id, _ = selected_ensembles.popitem()
        ensemble = load_ensemble(parent, ensemble_id)
        options = [
            {"label": parameter_key, "value": parameter_key}
            for parameter_key in ensemble.parameters
        ]
        prev_selection = [
            plot["name"] for plot in prev_plot_selection if plot["type"] == "parameter"
        ]
        return options, prev_selection

    @app.callback(
        Output({"index": MATCH, "type": parent.uuid("bincount-store")}, "data"),
        [Input({"index": MATCH, "type": parent.uuid("hist-bincount")}, "value")],
        [State({"index": MATCH, "type": parent.uuid("bincount-store")}, "data")],
    )
    def _update_bincount(hist_bincount, store_bincount):
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
        ],
        [
            State(parent.uuid("ensemble-selection-store"), "data"),
            State({"index": MATCH, "type": parent.uuid("parameter-id-store")}, "data"),
            State({"index": MATCH, "type": parent.uuid("bincount-store")}, "data"),
        ],
    )
    def _update_histogram(
        hist_check_values, _, selected_ensembles, parameter, bin_count
    ):
        if not selected_ensembles:
            raise PreventUpdate

        data = {}
        colors = {}
        priors = {}
        for ensemble_id, color in selected_ensembles.items():
            ensemble = load_ensemble(parent, ensemble_id)
            if parameter in ensemble.parameters:
                key = str(ensemble)
                parameter_model = ensemble.parameters[parameter]
                data[key] = parameter_model.data_df()
                colors[key] = color["color"]

                if parameter_model.priors and "prior" in hist_check_values:
                    priors[key] = (parameter_model.priors, colors[key])

        parent.parameter_plot = MultiHistogramPlotModel(
            data,
            colors=colors,
            hist="hist" in hist_check_values,
            kde="kde" in hist_check_values,
            priors=priors,
            bin_count=bin_count,
        )
        return parent.parameter_plot.repr, parent.parameter_plot.bin_count

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
    def _set_parameter_from_btn(parameter, plotting_options, selected_ensembles):
        has_priors = False
        for ensemble_id, _ in selected_ensembles.items():
            ensemble = load_ensemble(parent, ensemble_id)
            if parameter in ensemble.parameters:
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
