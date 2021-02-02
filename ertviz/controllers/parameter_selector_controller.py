import regex
import dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
from ertviz.models import (
    load_ensemble,
)


def _filter_match(filter, key):
    reg_exp = ".*" + ".*".join(filter.split())
    try:
        match = bool(regex.match(reg_exp, key))
    except:
        return False
    return match


def parameter_selector_controller(parent, app):
    @app.callback(
        [
            Output(parent.uuid("parameter-selector-multi"), "options"),
            Output(parent.uuid("parameter-selector-multi"), "value"),
        ],
        [
            Input(parent.uuid("ensemble-selection-store"), "data"),
            Input(parent.uuid("parameter-selector-filter"), "value"),
            Input(parent.uuid("parameter-deactivator"), "value"),
        ],
    )
    def update_parameters_options(selected_ensembles, filter_search, selected):
        if not selected_ensembles:
            raise PreventUpdate
        selected = [] if not selected else selected

        params_included = None
        for ensemble_id, _ in selected_ensembles.items():
            ensemble = load_ensemble(parent, ensemble_id)
            if bool(filter_search):
                parameters = set(
                    [
                        parameter_key
                        for parameter_key in ensemble.parameters
                        if _filter_match(filter_search, parameter_key)
                        and parameter_key not in selected
                    ]
                )
            else:
                parameters = set(
                    [
                        parameter_key
                        for parameter_key in ensemble.parameters
                        if parameter_key not in selected
                    ]
                )
            if params_included is None:
                params_included = parameters
            else:
                params_included = params_included.intersection(parameters)
        options = [
            {"label": parameter_key, "value": parameter_key}
            for parameter_key in params_included
        ]
        return options, selected

    @app.callback(
        Output(parent.uuid("parameter-selection-store"), "data"),
        [
            Input(parent.uuid("parameter-selector-multi"), "value"),
            Input(parent.uuid("parameter-selector-filter"), "n_submit"),
        ],
        [
            State(parent.uuid("parameter-deactivator"), "value"),
            State(parent.uuid("parameter-selector-multi"), "options"),
        ],
    )
    def update_parameter_selection(parameters, _, selected_params, par_opts):
        selected_params = [] if selected_params is None else selected_params
        selected_params = (
            [selected_params] if type(selected_params) == str else selected_params
        )

        parameters = [parameters] if type(parameters) == str else parameters

        ctx = dash.callback_context
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if triggered_id == parent.uuid("parameter-selector-filter"):
            parameters = [
                parm["value"]
                for parm in par_opts
                if parm["value"] not in selected_params
            ]
            if not bool(parameters):
                raise PreventUpdate
            return selected_params + parameters
        elif triggered_id == parent.uuid("parameter-selector-multi"):
            parameters = [
                parameter
                for parameter in parameters
                if parameter not in selected_params
            ]
            return selected_params + parameters

    @app.callback(
        [
            Output(parent.uuid("parameter-deactivator"), "options"),
            Output(parent.uuid("parameter-deactivator"), "value"),
        ],
        [
            Input(parent.uuid("parameter-selection-store"), "modified_timestamp"),
        ],
        [
            State(parent.uuid("parameter-selection-store"), "data"),
        ],
    )
    def update_parameter_selection(_, shown_parameters):
        shown_parameters = [] if shown_parameters is None else shown_parameters
        selected_opts = [{"label": param, "value": param} for param in shown_parameters]
        return selected_opts, shown_parameters
