import dash_html_components as html
import dash_core_components as dcc


def timeseries_view(parent):
    return [
        html.Div(
            [
                html.Div(
                    [
                        html.H5("Response"),
                        dcc.Dropdown(id=parent.uuid("response-selector")),
                    ],
                    style={
                        "width": "48%",
                    },
                ),
            ]
        ),
        dcc.Graph(id=parent.uuid("responses-graphic")),
    ]


def parameter_view(parent):
    return [
        html.Div(
            [
                html.Div(
                    [
                        html.H5("Parameter"),
                        dcc.Dropdown(id=parent.uuid("parameter-selector")),
                    ],
                    style={
                        "width": "48%",
                    },
                ),
            ]
        ),
        dcc.Graph(id=parent.uuid("paremeter-graphic")),
    ]
