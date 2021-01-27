import dash
import dash_html_components as html
import dash_core_components as dcc
import ertviz.assets as assets


def parallel_coordinates_view(parent):
    return html.Div(
        className="ert-view-container",
        children=[
            dcc.Graph(
                id={
                    "id": parent.uuid("parallel-coor"),
                    "type": parent.uuid("graph"),
                },
                className="ert-view-cell",
                config={"responsive": True},
            )
        ],
    )
