import dash
import dash_html_components as html
import dash_core_components as dcc
import ertviz.assets as assets


def parallel_coordinates_view(parent):
    return html.Div(
        [
            html.Div(
                [
                    html.Label("ParCoor:"),
                ],
                className="ert-graph-options",
            ),
            dcc.Graph(
                id={
                    "id": parent.uuid("parallel-coor"),
                    "type": parent.uuid("graph"),
                },
                className="ert-graph",
                config={"responsive": True},
            ),
        ],
        className="ert-graph-container",
    )
