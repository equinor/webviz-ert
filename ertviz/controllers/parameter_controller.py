import re
import dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
from ertviz.data_loader import get_parameters
from ertviz.controllers import parse_url_query


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


def parameter_controller(parent, app):
    @app.callback(
        Output(parent.uuid("parameter-selector"), "options"), [Input("url", "search")]
    )
    def update_parameter_options(search):
        queries = parse_url_query(search)
        if not "ensemble_id" in queries:
            return []
        ensemble_id = queries["ensemble_id"]
        parent.parameter_models = get_parameters(ensemble_id)
        options = [
            {"label": parameter_key, "value": parameter_key}
            for parameter_key in parent.parameter_models
        ]
        return options

    @app.callback(
        Output(parent.uuid("parameter-graph"), "data"),
        [Input(parent.uuid("parameter-selector"), "value")],
    )
    def _set_parameter(parameter):
        iterations = []
        values = []
        labels = []
        param = parent.parameter_models[parameter]
        iterations.append("name")
        values.append(param.realization_values)
        labels.append([f"Realization {real}" for real in param.realization_names])
        data = {"iterations": iterations, "values": values, "labels": labels}
        return data

    @app.callback(
        Output(parent.uuid("parameter-selector"), "value"),
        [
            Input(parent.uuid("prev-btn"), "n_clicks"),
            Input(parent.uuid("next-btn"), "n_clicks"),
        ],
        [
            State(parent.uuid("parameter-selector"), "value"),
            State(parent.uuid("parameter-selector"), "options"),
        ],
    )
    def _set_parameter_from_btn(_prev_click, _next_click, parameter, parameter_options):

        ctx = dash.callback_context.triggered
        if not ctx:
            raise PreventUpdate

        callback = ctx[0]["prop_id"]
        if callback == f"{parent.uuid('prev-btn')}.n_clicks":
            parameter = _prev_value(
                parameter, [option["value"] for option in parameter_options]
            )
        elif callback == f"{parent.uuid('next-btn')}.n_clicks":
            parameter = next_value(
                parameter, [option["value"] for option in parameter_options]
            )
        return parameter
