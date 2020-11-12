import dash
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_core_components as dcc
from webviz_config import WebvizPluginABC
import webviz_subsurface_components as wsc
import ertviz.assets as assets


def _make_buttons(prev_id, next_id):
    return html.Div(
        className="ert-parameter-navigator",
        children=[
            html.Button(
                id=prev_id,
                className="ert-button",
                children="⬅",
            ),
            html.Button(
                id=next_id,
                className="ert-button",
                children="➡",
            ),
        ],
    )


def _make_checkboxes(hist_check_id):
    return html.Div(
        dcc.Checklist(
            id=hist_check_id,
            options=[
                {"label": "histogram", "value": "hist"},
                {"label": "kde", "value": "kde"},
            ],
            value=["hist", "kde"],
        )
    )


def parameter_view(parent):
    return [
        html.Div(
            children=[
                html.H5("Parameter distribution:"),
                html.Div(
                    className="ert-parameter-viewer ert-dropdown",
                    children=[
                        dcc.Dropdown(
                            id=parent.uuid("parameter-selector"),
                        ),
                        _make_buttons(parent.uuid("prev-btn"), parent.uuid("next-btn")),
                    ],
                ),
                _make_checkboxes(parent.uuid("hist-check")),
                dcc.Graph(
                    id={
                        "id": parent.uuid("parameter-scatter"),
                        "type": parent.uuid("graph"),
                    }
                ),
            ],
        )
    ]
