import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc


def response_view(parent, index=0):
    return [
        dcc.Store(
            id={"index": index, "type": parent.uuid("response-id-store")}, data=index
        ),
        dbc.Row(
            className="ert-plot-options",
            children=[
                dbc.Col(
                    [html.H4(index)],
                    align="center",
                ),
                dbc.Col(
                    [
                        html.Label("Graph Type:", className="ert-label"),
                    ],
                    width="auto",
                    align="center",
                ),
                dbc.Col(
                    [
                        dcc.RadioItems(
                            options=[
                                {"label": key, "value": key}
                                for key in ["Function plot", "Statistics"]
                            ],
                            value="Function plot",
                            id={"index": index, "type": parent.uuid("plot-type")},
                            persistence="session",
                        ),
                    ],
                    align="center",
                ),
            ],
        ),
        dcc.Graph(
            id={
                "index": index,
                "id": parent.uuid("response-graphic"),
                "type": parent.uuid("graph"),
            },
            config={"responsive": True},
        ),
    ]
