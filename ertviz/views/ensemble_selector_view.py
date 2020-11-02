import dash_html_components as html
import dash_core_components as dcc
import dash_cytoscape as cyto

cyto.load_extra_layouts()

cyto_style = {"width": "100%", "height": "200px"}


def ensemble_selector_view(parent):
    return [
        dcc.Dropdown(
            id="dropdown-layout",
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
                    style=cyto_style,
                    stylesheet=[
                        {"selector": "node", "style": {"label": "data(label)"}},
                        {
                            "selector": "edge",
                            "style": {"line-color": "rgba(55,55,55,0.8)"},
                        },
                        {
                            "selector": "node:selected",
                            "style": {
                                "label": "data(label)",
                                "background-color": "data(color)",
                            },
                        },
                    ],
                )
            ]
        ),
        dcc.Store(id=parent.uuid("ensemble-selection-store")),
    ]
