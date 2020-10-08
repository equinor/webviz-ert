import dash_html_components as html
import dash_core_components as dcc
from .paremeter_view import parameter_view


def response_view(parent):
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
