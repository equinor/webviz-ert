from typing import List, Dict, Any
from webviz_ert.plugins._webviz_ert import WebvizErtPluginABC
import dash
from dash.dependencies import Input, Output, State
from webviz_ert.data_loader import get_ensembles
from webviz_ert.models import load_ensemble


def get_non_selected_options(store: Dict[str, List]) -> List[Dict[str, str]]:
    _options = []
    for option in store["options"]:
        if option not in store["selected"]:
            _options.append(option)
    return _options


def ensemble_list_selector_controller(
    parent: WebvizErtPluginABC, app: dash.Dash
) -> None:
    @app.callback(
        [
            Output(parent.uuid("selected-ensemble-dropdown"), "options"),
            Output(parent.uuid("selected-ensemble-dropdown"), "value"),
            Output(parent.uuid("ensemble-multi-selector"), "options"),
            Output(parent.uuid("ensemble-selection-store"), "data"),
        ],
        [
            Input(parent.uuid("ensemble-multi-selector"), "value"),
            Input(parent.uuid("selected-ensemble-dropdown"), "value"),
        ],
        [
            State(parent.uuid("selected-ensemble-dropdown"), "options"),
            State(parent.uuid("selected-ensemble-dropdown"), "value"),
            State(parent.uuid("ensemble-multi-selector"), "options"),
            State(parent.uuid("ensemble-selection-store"), "data"),
        ],
    )
    def set_callback(
        _input_ensemble_selector: List[str],
        _: List[str],
        selected_ens_options: List[Dict],
        selected_ens_value: List[str],
        ens_selector_options: List[Dict[str, str]],
        ensemble_selection_store: Dict[str, List],
    ) -> List[Any]:
        ctx = dash.callback_context
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if not triggered_id and not ensemble_selection_store:
            ensemble_selection_store = {"options": [], "selected": []}

            if not parent.get_ensembles():
                ensemble_dict = get_ensembles(project_id=parent.project_identifier)
                for ensemble_schema in ensemble_dict:
                    ensemble_id = ensemble_schema["id"]
                    load_ensemble(parent, ensemble_id)

            for ens_id, ensemble in parent.get_ensembles().items():
                element = {"label": ensemble.name, "value": ensemble.id}
                ensemble_selection_store["options"].append(element)

        if triggered_id == parent.uuid("ensemble-multi-selector"):
            selected_list_elem = _input_ensemble_selector[0]
            element = next(
                op for op in ens_selector_options if op["value"] == selected_list_elem
            )
            ensemble_selection_store["selected"].append(element)

        if triggered_id == parent.uuid("selected-ensemble-dropdown"):
            element = next(
                op
                for op in selected_ens_options
                if op["value"] not in selected_ens_value
            )
            ensemble_selection_store["selected"].remove(element)

        ens_selector_options = get_non_selected_options(ensemble_selection_store)
        selected_ens_options = ensemble_selection_store["selected"]
        selected_ens_value = [option["value"] for option in selected_ens_options]
        return [
            selected_ens_options,
            selected_ens_value,
            ens_selector_options,
            ensemble_selection_store,
        ]
