import dash
import dash_html_components as html
import dash_core_components as dcc
import ertviz.assets as assets


def parameter_view(parent):
    return [
        html.H5("Parameter distribution"),
        html.Div(
            className="ert-dropdown-container",
            children=[
                html.Label("Parameter", className="ert-label"),
                dcc.Dropdown(
                    id=parent.uuid("parameter-selector"), className="ert-dropdown"
                ),
                html.Div(
                    [
                        html.Button(
                            id=parent.uuid("prev-btn"),
                            children="⬅",
                        )
                    ],
                    className="ert-button",
                ),
                html.Div(
                    [
                        html.Button(
                            id=parent.uuid("next-btn"),
                            children="➡",
                        )
                    ],
                    className="ert-button",
                ),
            ],
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Label("Plots:"),
                        dcc.Checklist(
                            id=parent.uuid("hist-check"),
                            options=[
                                {"label": "histogram", "value": "hist"},
                                {"label": "kde", "value": "kde"},
                            ],
                            value=["hist", "kde"],
                        ),
                    ],
                    className="ert-graph-options",
                ),
                dcc.Graph(
                    id={
                        "id": parent.uuid("parameter-scatter"),
                        "type": parent.uuid("graph"),
                    },
                    className="ert-graph",
                ),
            ],
            className="ert-graph-container",
        ),
    ]
