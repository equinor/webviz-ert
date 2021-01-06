from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
from ertviz.models import (
    load_ensemble,
)


def parameter_selector_controller(parent, app):
    @app.callback(
        Output(parent.uuid("parameter-selector-multi"), "options"),
        [
            Input(parent.uuid("ensemble-selection-store"), "data"),
            Input(parent.uuid("parameter-selector-filter"), "value"),
        ],
    )
    def update_parameters_options(selected_ensembles, filter_search):
        if not selected_ensembles:
            raise PreventUpdate

        ensemble_id, _ = selected_ensembles.popitem()
        ensemble = load_ensemble(parent, ensemble_id)
        if bool(filter_search):
            options = [
                {"label": parameter_key, "value": parameter_key}
                for parameter_key in ensemble.parameters
                if filter_search in parameter_key
            ]
        else:
            options = [
                {"label": parameter_key, "value": parameter_key}
                for parameter_key in ensemble.parameters
            ]
        return options
