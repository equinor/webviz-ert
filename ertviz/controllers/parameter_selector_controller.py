import re
import dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
from ertviz.models import (
    load_ensemble,
)

from ertviz.controllers import parameter_options, response_options


def _filter_match(filter, key):
    reg_exp = ".*" + ".*".join(filter.split())
    try:
        match = bool(re.match(reg_exp, key, re.IGNORECASE))
    except:
        return False
    return match


def parameter_selector_controller(
    parent, app, suffix="", union_keys=True, extra_input=False
):
    parameter_selector_multi_id = parent.uuid(f"parameter-selector-multi-{suffix}")
    parameter_type_store_id = parent.uuid(f"parameter-type-store-{suffix}")
    parameter_selector_filter_id = parent.uuid(f"parameter-selector-filter-{suffix}")
    parameter_deactivator_id = parent.uuid(f"parameter-deactivator-{suffix}")
    parameter_selection_store_id = parent.uuid(f"parameter-selection-store-{suffix}")
    options_inputs = [
        Input(parent.uuid("ensemble-selection-store"), "data"),
        Input(parameter_selector_filter_id, "value"),
        Input(parameter_deactivator_id, "value"),
    ]
    if extra_input:
        options_inputs.extend(
            [Input(parent.uuid("response-observations-check"), "value")]
        )

    @app.callback(
        [
            Output(parameter_selector_multi_id, "options"),
            Output(parameter_selector_multi_id, "value"),
        ],
        options_inputs,
        [State(parameter_type_store_id, "data")],
    )
    def update_parameters_options(selected_ensembles, filter_search, selected, *args):
        if not selected_ensembles:
            raise PreventUpdate
        store_type = args[0]
        response_filter = []
        if extra_input:
            store_type = args[1]
            response_filter = args[0]
        selected = [] if not selected else selected
        ensembles = [
            load_ensemble(parent, ensemble_id) for ensemble_id in selected_ensembles
        ]
        options = None
        if store_type == "parameter":
            options = parameter_options(ensembles, union_keys=union_keys)
        elif store_type == "response":
            options = response_options(response_filter, ensembles)
        else:
            raise ValueError(f"Undefined parameter type {store_type}")

        options = [option for option in options if option["value"] not in selected]
        if bool(filter_search):
            options = [
                option
                for option in options
                if _filter_match(filter_search, option["value"])
            ]

        return options, selected

    @app.callback(
        Output(parameter_selection_store_id, "data"),
        [
            Input(parameter_selector_multi_id, "value"),
            Input(parameter_selector_filter_id, "n_submit"),
        ],
        [
            State(parameter_deactivator_id, "value"),
            State(parameter_selector_multi_id, "options"),
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
        if triggered_id == parameter_selector_filter_id:
            parameters = [
                parm["value"]
                for parm in par_opts
                if parm["value"] not in selected_params
            ]
            if not bool(parameters):
                raise PreventUpdate
            return selected_params + parameters
        elif triggered_id == parameter_selector_multi_id:
            parameters = [
                parameter
                for parameter in parameters
                if parameter not in selected_params
            ]
            return selected_params + parameters

    @app.callback(
        [
            Output(parameter_deactivator_id, "options"),
            Output(parameter_deactivator_id, "value"),
        ],
        [
            Input(parameter_selection_store_id, "modified_timestamp"),
        ],
        [
            State(parameter_selection_store_id, "data"),
        ],
    )
    def update_parameter_selection(_, shown_parameters):
        shown_parameters = [] if shown_parameters is None else shown_parameters
        selected_opts = [{"label": param, "value": param} for param in shown_parameters]
        return selected_opts, shown_parameters

    container_parameter_selector_multi_id = parent.uuid(
        f"container-parameter-selector-multi-{suffix}"
    )
    parameter_selector_button_id = parent.uuid(f"parameter-selector-button-{suffix}")

    @app.callback(
        Output(container_parameter_selector_multi_id, "className"),
        [
            Input(parameter_selector_button_id, "n_clicks"),
        ],
        [
            State(container_parameter_selector_multi_id, "className"),
        ],
    )
    def toggle_selector_visibility(_, class_name):
        ctx = dash.callback_context
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if triggered_id == parameter_selector_button_id:
            if class_name == "ert-parameter-selector-container-hide":
                class_name = "ert-parameter-selector-container-show"
            else:
                class_name = "ert-parameter-selector-container-hide"
        return class_name
