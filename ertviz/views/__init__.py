import dash_html_components as html
import dash_core_components as dcc
from .paremeter_view import parameter_view
from .ensemble_selector_view import ensemble_selector_view


def response_view(parent):
    return [
        html.Div(
            [
                html.Div(
                    className="ert-dropdown",
                    children=[
                        html.H5("Response"),
                        dcc.Dropdown(id=parent.uuid("response-selector")),
                    ],
                ),
                html.Div(
                    children=[
                        html.Label("Select Graph Type:"),
                        dcc.RadioItems(
                            options=[
                                {"label": key, "value": key}
                                for key in ["Function plot", "Statistics"]
                            ],
                            value="Function plot",
                            id=parent.uuid("plot-type"),
                        ),
                    ]
                ),
            ]
        ),
        dcc.Graph(
            id={"id": parent.uuid("response-graphic"), "type": parent.uuid("graph")}
        ),
    ]
