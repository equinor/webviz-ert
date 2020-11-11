import dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State

from ertviz.controllers import parse_url_query
from ertviz.models import EnsembleModel, MultiHistogramPlotModel
from ertviz.data_loader import get_ensemble_url


def _prev_value(current_value, options):
    try:
        index = options.index(current_value)
    except ValueError:
        index = None
    if index > 0:
        return options[index - 1]
    return current_value


def next_value(current_value, options):
    try:
        index = options.index(current_value)
    except ValueError:
        index = None
    if index < len(options) - 1:
        return options[index + 1]
    return current_value


def multi_parameter_controller(parent, app):
    @app.callback(
        Output(parent.uuid("parameter-selector"), "options"),
        [
            Input(parent.uuid("ensemble-selection-store"), "data"),
        ],
    )
    def update_parameter_options(selected_ensembles):
        if not selected_ensembles:
            raise PreventUpdate
        ensemble_id, _ = selected_ensembles.popitem()
        ensemble = parent.ensembles.get(ensemble_id, EnsembleModel(ref_url=ensemble_id))
        parent.ensembles[ensemble_id] = ensemble
        parent.parameter_models[ensemble_id] = ensemble.parameters
        options = [
            {"label": parameter_key, "value": parameter_key}
            for parameter_key in parent.parameter_models[ensemble_id]
        ]
        print(options)
        return options

    @app.callback(
        Output(
            {"id": parent.uuid("parameter-scatter"), "type": parent.uuid("graph")},
            "figure",
        ),
        [
            Input(parent.uuid("parameter-selector"), "value"),
            Input(parent.uuid("hist-check"), "value"),
        ],
        [State(parent.uuid("ensemble-selection-store"), "data")],
    )
    def _update_histogram(parameter, hist_check_values, selected_ensembles):
        if not selected_ensembles:
            raise PreventUpdate
        data = {}
        for ensemble_id in selected_ensembles:
            if parameter in parent.parameter_models[ensemble_id]:
                data[parent.ensembles[ensemble_id]._name] = parent.parameter_models[
                    ensemble_id
                ][parameter].data_df()

        parent.parameter_plot = MultiHistogramPlotModel(
            data,
            hist="hist" in hist_check_values,
            kde="kde" in hist_check_values,
        )
        return parent.parameter_plot.repr

    @app.callback(
        Output(parent.uuid("parameter-selector"), "value"),
        [
            Input(parent.uuid("prev-btn"), "n_clicks"),
            Input(parent.uuid("next-btn"), "n_clicks"),
            Input(parent.uuid("parameter-selector"), "options"),
        ],
        [
            State(parent.uuid("parameter-selector"), "value"),
        ],
    )
    def _set_parameter_from_btn(_prev_click, _next_click, parameter_options, parameter):

        ctx = dash.callback_context.triggered

        callback = ctx[0]["prop_id"]
        if callback == f"{parent.uuid('prev-btn')}.n_clicks":
            parameter = _prev_value(
                parameter, [option["value"] for option in parameter_options]
            )
        elif callback == f"{parent.uuid('next-btn')}.n_clicks":
            parameter = next_value(
                parameter, [option["value"] for option in parameter_options]
            )
        elif parameter_options:
            parameter = parameter_options[0]["value"]
        else:
            raise PreventUpdate
        return parameter
