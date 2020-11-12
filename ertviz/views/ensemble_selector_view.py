import dash_html_components as html
import dash_core_components as dcc
import dash_cytoscape as cyto
import ertviz.assets as assets


cyto.load_extra_layouts()


def ensemble_selector_view(parent):
    return [
        dcc.Dropdown(
            id="dropdown-layout",
            className="ert-dropdown",
            options=[
                {"label": "random", "value": "random"},
                {"label": "grid", "value": "grid"},
                {"label": "circle", "value": "circle"},
                {"label": "concentric", "value": "concentric"},
                {"label": "breadthfirst", "value": "breadthfirst"},
                {"label": "cose", "value": "cose"},
                {"label": "cose-bilkent", "value": "cose-bilkent"},
                {"label": "dagre", "value": "dagre"},
                {"label": "cola", "value": "cola"},
                {"label": "klay", "value": "klay"},
                {"label": "spread", "value": "spread"},
                {"label": "euler", "value": "euler"},
            ],
            value="cola",
            clearable=False,
        ),
        html.Div(
            [
                cyto.Cytoscape(
                    id=parent.uuid("ensemble-selector"),
                    layout={"name": "grid"},
                    className="ert-ensemble-selector",
                    stylesheet=assets.ERTSTYLE["ensemble-selector"]["stylesheet"],
                )
            ]
        ),
        dcc.Store(id=parent.uuid("ensemble-selection-store")),
    ]
