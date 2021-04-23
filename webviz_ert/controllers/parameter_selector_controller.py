import re
import dash
from typing import List, Any, Tuple, Dict, Optional, Mapping
from webviz_ert.plugins._webviz_ert import WebvizErtPluginABC
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
from webviz_ert.models import (
    load_ensemble,
)

from webviz_ert.controllers import parameter_options, response_options


def _filter_match(filter: str, key: str) -> bool:
    reg_exp = ".*" + ".*".join(filter.split())
    try:
        match = bool(re.match(reg_exp, key, re.IGNORECASE))
    except:
        return False
    return match


def parameter_selector_controller(
    parent: WebvizErtPluginABC,
    app: dash.Dash,
    suffix: str = "",
    union_keys: bool = True,
    extra_input: bool = False,
) -> None:
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
    def update_parameters_options(
        selected_ensembles: Optional[Mapping[str, Dict]],
        filter_search: str,
        selected: Optional[List[str]],
        *args: List[str],
    ) -> Tuple[List[Dict], List[str]]:
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
    def update_parameter_selection(
        parameters: List[str],
        _: int,
        selected_params: Optional[List[str]],
        par_opts: List[Dict],
    ) -> Optional[List[str]]:
        selected_params = [] if not selected_params else selected_params
        parameters = [] if not parameters else parameters

        ctx = dash.callback_context
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if triggered_id == parameter_selector_filter_id:
            parameters = [
                parm["value"]
                for parm in par_opts
                if parm["value"] not in selected_params
            ]
            if not parameters:
                raise PreventUpdate
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
    def update_parameter_options(
        _: Any, shown_parameters: Optional[List[str]]
    ) -> Tuple[List[Dict], List[str]]:
        shown_parameters = [] if not shown_parameters else shown_parameters
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
    def toggle_selector_visibility(_: int, class_name: str) -> str:
        ctx = dash.callback_context
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if triggered_id == parameter_selector_button_id:
            if class_name == "ert-parameter-selector-container-hide":
                class_name = "ert-parameter-selector-container-show"
            else:
                class_name = "ert-parameter-selector-container-hide"
        return class_name
