import dash_html_components as html
import dash_core_components as dcc
from .paremeter_view import parameter_view
from .ensemble_selector_view import ensemble_selector_view


def response_view(parent):
    return [
        html.Div(
            [
                html.Div(
                    children=[
                        html.Label("Select Graph Type"),
                        dcc.RadioItems(
                            options=["Function plot", "Statistics"],
                            value="Function plot",
                            id=parent.uuid("plot-type"),
                        ),
                    ]
                ),
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
        dcc.Graph(
            id={"id": parent.uuid("response-graphic"), "type": parent.uuid("graph")}
        ),
    ]
