import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from ertviz.data_loader import get_ensembles
from ertviz.models import EnsembleModel
import ertviz.assets as assets


def _construct_graph(ensembles):

    roots = [
        ensemble
        for ensemble_id, ensemble in ensembles.items()
        if ensemble.parent == None
    ]

    datas = []
    queue = []
    for index, ensemble in enumerate(roots):
        queue.append(ensemble)

    def _construct_node(ensemble):
        return {
            "data": {
                "id": ensemble.id,
                "label": ensemble._name,
            }
        }

    def _construct_edge(ensemble_src, ensemble_target):
        return {
            "data": {
                "source": ensemble_src.id,
                "target": ensemble_target.id,
            }
        }

    while queue:
        ensemble = queue.pop(-1)
        datas.append(_construct_node(ensemble))
        nr_of_children = len(ensemble.children)
        for index, child in enumerate(ensemble.children):
            datas.append(_construct_edge(ensemble, child))
            queue.append(child)
    return datas


def ensemble_selector_controller(parent, app):
    @app.callback(
        Output(parent.uuid("ensemble-selector"), "layout"),
        [Input(parent.uuid("dropdown-layout"), "value")],
    )
    def update_cytoscape_layout(layout):
        return {"name": layout}

    @app.callback(
        Output(parent.uuid("ensemble-selector"), "elements"),
        [
            Input("url", "pathname"),
            Input(parent.uuid("ensemble-selection-store"), "data"),
        ],
        [
            State(parent.uuid("ensemble-selector"), "elements"),
        ],
    )
    def update_ensemble_selector(query, selected_ensembles, elements):
        ctx = dash.callback_context
        select_update = ctx.triggered[0]["prop_id"].split(".")[0] == parent.uuid(
            "ensemble-selection-store"
        )
        if select_update:
            datas = elements
            for element in datas:
                element["data"].update(
                    selected_ensembles.get(element["data"]["id"], {})
                )
        else:
            ensemble_dict = get_ensembles()
            for ensemble_schema in ensemble_dict:
                ensemble_id = ensemble_schema["ref_url"]
                if ensemble_id not in parent.ensembles:
                    parent.ensembles[ensemble_id] = EnsembleModel(ref_url=ensemble_id)
            datas = _construct_graph(parent.ensembles)
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
