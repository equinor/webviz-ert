import dash

from typing import List, Any, Tuple, Dict, Optional
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State

from webviz_ert.plugins import WebvizErtPluginABC
from webviz_ert.models import (
    load_ensemble,
)
from webviz_ert.controllers import parameter_options, response_options
from webviz_ert.models.data_model import DataType


def _filter_match(_filter: str, key: str) -> bool:
    return _filter.lower() in key.lower()


def parameter_selector_controller(
    parent: WebvizErtPluginABC,
    app: dash.Dash,
    data_type: DataType,
    union_keys: bool = True,
    extra_input: bool = False,
) -> None:
    parameter_selector_multi_id = parent.uuid(f"parameter-selector-multi-{data_type}")
    parameter_selector_filter_id = parent.uuid(f"parameter-selector-filter-{data_type}")
    parameter_deactivator_id = parent.uuid(f"parameter-deactivator-{data_type}")
    parameter_selection_store_id = parent.uuid(f"parameter-selection-store-{data_type}")
    options_inputs = [
        Input(parent.uuid("selected-ensemble-dropdown"), "value"),
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
    )
    def update_parameters_options(
        selected_ensembles: List[str],
        filter_search: str,
        selected: Optional[List[str]],
        *args: List[str],
    ) -> Tuple[List[Dict], Optional[List[str]]]:
        if not selected_ensembles:
            # Reset selection list
            return [], []

        response_filter = []
        if extra_input:
            response_filter = args[0]
        selected_set = set() if not selected else set(selected)
        ensembles = [
            load_ensemble(parent, ensemble_id) for ensemble_id in selected_ensembles
        ]
        if data_type == DataType.PARAMETER:
            options = parameter_options(ensembles, union_keys=union_keys)
        elif data_type == DataType.RESPONSE:
            options = response_options(response_filter, ensembles)
        else:
            raise ValueError(f"Undefined parameter type {data_type}")

        options = options.difference(selected_set)
        if filter_search:
            options = {name for name in options if _filter_match(filter_search, name)}

        return [{"label": name, "value": name} for name in sorted(options)], selected

    @app.callback(
        Output(parameter_selection_store_id, "data"),
        [
            Input(parameter_selector_multi_id, "value"),
            Input(parameter_selector_filter_id, "n_submit"),
            Input(parent.uuid("selected-ensemble-dropdown"), "value"),
        ],
        State(parameter_deactivator_id, "value"),
    )
    def update_parameter_selection(
        parameters: List[str],
        _: int,
        selected_ensembles: List[str],
        selected_params: Optional[List[str]],
    ) -> Optional[List[str]]:
        stored_parameters = None
        ctx = dash.callback_context
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if triggered_id == parameter_selector_filter_id:
            # Prevent selecting everything from the search result on enter
            raise PreventUpdate
        elif triggered_id == parent.uuid("selected-ensemble-dropdown"):
            if selected_ensembles is None or selected_ensembles == []:
                stored_parameters = []
            else:
                raise PreventUpdate
        elif triggered_id == parameter_selector_multi_id:
            selected_params = [] if not selected_params else selected_params
            parameters = (
                []
                if not parameters
                else [
                    parameter
                    for parameter in parameters
                    if parameter not in selected_params
                ]
            )
            stored_parameters = selected_params + parameters

        parent.save_state(f"{data_type}", stored_parameters)

        return stored_parameters

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
        f"container-parameter-selector-multi-{data_type}"
    )
    parameter_selector_button_id = parent.uuid(f"parameter-selector-button")

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
