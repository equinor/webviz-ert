import dash_html_components as html
import dash_core_components as dcc
from .paremeter_view import parameter_view
from .ensemble_selector_view import ensemble_selector_view


def response_view(parent):
    return [
        html.H5("Response plots"),
        html.Div(
            className="ert-dropdown-container",
            children=[
                html.Label("Response", className="ert-label"),
                dcc.Dropdown(
                    id=parent.uuid("response-selector"),
                    className="ert-dropdown",
                ),
            ],
        ),
        html.Div(
            [
                html.Div(
                    className="ert-graph-options",
                    children=[
                        html.Label("Graph Type:"),
                        dcc.RadioItems(
                            options=[
                                {"label": key, "value": key}
                                for key in ["Function plot", "Statistics"]
                            ],
                            value="Function plot",
                            id=parent.uuid("plot-type"),
                        ),
                    ],
                ),
                dcc.Graph(
                    id={
                        "id": parent.uuid("response-graphic"),
                        "type": parent.uuid("graph"),
                    },
                    className="ert-graph",
                ),
            ],
            className="ert-graph-container",
        ),
    ]
