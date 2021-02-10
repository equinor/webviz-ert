import dash_html_components as html
import dash_core_components as dcc


def correlation_view(parent, id_view):
    return html.Div(
        className="ert-view-container",
        children=[
            dcc.Graph(
                id={
                    "id": id_view,
                    "type": parent.uuid("graph"),
                },
                className="ert-view-cell",
                config={"responsive": True},
            )
        ],
    )
