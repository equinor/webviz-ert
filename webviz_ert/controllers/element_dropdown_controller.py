import dash

from typing import List, Tuple, Dict, Optional, Any
from dash.dependencies import Input, Output, State

from webviz_ert.models import DataType
from webviz_ert.plugins import WebvizErtPluginABC
from webviz_ert.models import load_ensemble
from webviz_ert.controllers import parameter_options, response_options


def element_dropdown_controller(
    parent: WebvizErtPluginABC,
    app: dash.Dash,
    data_type: DataType,
) -> None:
    @app.callback(
        [
            Output(parent.uuid(f"element-dropdown-{data_type}"), "options"),
            Output(parent.uuid(f"element-dropdown-{data_type}"), "value"),
            Output(parent.uuid(f"element-dropdown-store-{data_type}"), "data"),
        ],
        [
            Input(parent.uuid("ensemble-selection-store"), "modified_timestamp"),
            Input(parent.uuid(f"element-dropdown-{data_type}"), "value"),
        ],
        [
            State(parent.uuid(f"element-dropdown-store-{data_type}"), "data"),
            State(parent.uuid("ensemble-selection-store"), "data"),
        ],
    )
    def set_callbacks(
        _: Any,
        selected: Optional[str],
        selected_store: Optional[str],
        ensemble_selection_store: Dict[str, List],
    ) -> Tuple[List[Dict], Optional[str], Optional[str]]:

        if not ensemble_selection_store or not ensemble_selection_store["selected"]:
            return [], None, None

        selected_ensembles = [
            selection["value"] for selection in ensemble_selection_store["selected"]
        ]

        ensembles = [
            load_ensemble(parent, ensemble_id) for ensemble_id in selected_ensembles
        ]
        if data_type == DataType.PARAMETER:
            options = parameter_options(ensembles, union_keys=False)
        elif data_type == DataType.RESPONSE:
            options = response_options(response_filters=[], ensembles=ensembles)
        else:
            raise ValueError(f"Undefined data type {data_type}")

        element_options = [{"label": name, "value": name} for name in sorted(options)]

        # Keep track of selected element for the session
        if not selected and selected_store is not None:
            selected = selected_store

        return element_options, selected, selected
