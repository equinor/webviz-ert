import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from ertviz.models import list_ensembles, load_ensemble
import ertviz.assets as assets


def _construct_graph(ensembles):

    queue = [
        ensemble
        for ensemble_id, ensemble in ensembles.items()
        if ensemble.parent == None
    ]

    datas = []

    def _construct_node(ensemble):
        return {
            "data": {
                "id": str(ensemble.id),
                "label": str(ensemble),
                "color": assets.ERTSTYLE["ensemble-selector"]["default_color"],
            },
        }

    def _construct_edge(ensemble_src, ensemble_target):
        return {
            "data": {
                "source": str(ensemble_src.id),
                "target": str(ensemble_target.id),
            }
        }

    while queue:
        ensemble = queue.pop(-1)
        datas.append(_construct_node(ensemble))
        for child in ensemble.children:
            datas.append(_construct_edge(ensemble, child))
            queue.append(child)
    return datas


def ensemble_selector_controller(parent, app):
    @app.callback(
        Output(parent.uuid("ensemble-selector"), "elements"),
        [
            Input(parent.uuid("ensemble-selection-store"), "data"),
            Input(parent.uuid("ensemble-selector-button"), "n_clicks"),
        ],
        [
            State(parent.uuid("ensemble-selector"), "elements"),
        ],
    )
    def update_ensemble_selector_graph(selected_ensembles, _, elements):
        selected_ensembles = {} if selected_ensembles is None else selected_ensembles
        ctx = dash.callback_context
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if (
            triggered_id == parent.uuid("ensemble-selection-store")
            and elements is not None
        ):
            datas = elements
        else:
            ensembles = list_ensembles(parent)
            for ens in ensembles:
                load_ensemble(parent, ens.id)
            datas = _construct_graph(parent.ensembles)

        for element in datas:

            if "id" in element["data"]:
                element["data"].update(
                    selected_ensembles.get(element["data"]["id"], {})
                )
                element["selected"] = element["data"]["id"] in selected_ensembles
        return datas

    @app.callback(
        Output(parent.uuid("ensemble-selection-store"), "data"),
        [
            Input(parent.uuid("ensemble-selector"), "selectedNodeData"),
        ],
    )
    def update_ensemble_selection(selected_nodes):
        color_wheel = assets.ERTSTYLE["ensemble-selector"]["color_wheel"]
        if selected_nodes is None:
            raise PreventUpdate
        data = {
            ensemble["id"]: {
                "color": color_wheel[index % len(color_wheel)],
            }
            for index, ensemble in enumerate(selected_nodes)
        }

        return data

    @app.callback(
        [
            Output(parent.uuid("ensemble-selector"), "className"),
            Output(parent.uuid("ensemble-selector-container"), "className"),
            Output(parent.uuid("ensemble-selector-button"), "children"),
            Output(parent.uuid("ensemble-view-store"), "data"),
        ],
        [
            Input(parent.uuid("ensemble-selector-button"), "n_clicks"),
        ],
        [
            State(parent.uuid("ensemble-selector"), "className"),
            State(parent.uuid("ensemble-selector-container"), "className"),
            State(parent.uuid("ensemble-view-store"), "data"),
        ],
    )
    def update_ensemble_selector_view_size(
        _, class_name, class_name_container, maximized
    ):

        ctx = dash.callback_context
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if triggered_id == parent.uuid("ensemble-selector-button"):
            maximized = not maximized

        if maximized:
            old_class_name = "ert-ensemble-selector-small"
            new_class_name = "ert-ensemble-selector-large"
            old_container_class_name = "ert-ensemble-selector-container-small"
            new_container_class_name = "ert-ensemble-selector-container-large"
            new_button_text = "Minimize"
        else:
            old_class_name = "ert-ensemble-selector-large"
            new_class_name = "ert-ensemble-selector-small"
            old_container_class_name = "ert-ensemble-selector-container-large"
            new_container_class_name = "ert-ensemble-selector-container-small"
            new_button_text = "Expand"

        return [
            class_name.replace(old_class_name, new_class_name),
            class_name_container.replace(
                old_container_class_name, new_container_class_name
            ),
            new_button_text,
            maximized,
        ]
