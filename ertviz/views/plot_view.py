import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc


def plot_view_header(parent):
    return [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("Responses", className="ert-label"),
                        dcc.Dropdown(
                            id=parent.uuid("response-selector"),
                            className="ert-dropdown",
                            multi=True,
                        ),
                        dcc.Checklist(
                            id=parent.uuid("response-observations-check"),
                            options=[
                                {
                                    "label": "Show only responses with observations",
                                    "value": "obs",
                                },
                            ],
                            value=[],
                        ),
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        html.Label("Parameters", className="ert-label"),
                        dcc.Dropdown(
                            id=parent.uuid("parameter-selector"),
                            className="ert-dropdown",
                            multi=True,
                        ),
                    ],
                    width=6,
                ),
            ]
        ),
        dcc.Store(id=parent.uuid("plot-selection-store"), storage_type="session"),
    ]


def plot_view_body(parent):
    return [
        html.Div(id=parent.uuid("plotting-content")),
        dcc.Store(id=parent.uuid("plotting-content-store"), storage_type="session"),
    ]
