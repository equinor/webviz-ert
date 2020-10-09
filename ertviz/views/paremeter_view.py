import dash
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_core_components as dcc
from webviz_config import WebvizPluginABC
import webviz_subsurface_components as wsc


def _set_grid_layout(columns):
    return {
        "display": "grid",
        "alignContent": "space-around",
        "justifyContent": "space-between",
        "gridTemplateColumns": f"{columns}",
    }


def _make_buttons(prev_id, next_id):
    return html.Div(
        style=_set_grid_layout("1fr 1fr"),
        children=[
            html.Button(
                id=prev_id,
                style={
                    "fontSize": "2rem",
                    "paddingLeft": "5px",
                    "paddingRight": "5px",
                },
                children="⬅",
            ),
            html.Button(
                id=next_id,
                style={
                    "fontSize": "2rem",
                    "paddingLeft": "5px",
                    "paddingRight": "5px",
                },
                children="➡",
            ),
        ],
    )


def parameter_view(parent):
    return [
        html.Div(
            children=[
                html.Span("Parameter distribution:", style={"font-weight": "bold"}),
                html.Div(
                    style=_set_grid_layout("8fr 1fr 2fr"),
                    children=[
                        dcc.Dropdown(
                            id=parent.uuid("parameter-selector"),
                        ),
                        _make_buttons(parent.uuid("prev-btn"), parent.uuid("next-btn")),
                    ],
                ),
                dcc.Graph(
                    id={
                        "id": parent.uuid("parameter-scatter"),
                        "type": parent.uuid("graph"),
                    }
                ),
            ],
        )
    ]
