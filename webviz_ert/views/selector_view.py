from dash.development.base_component import Component
from webviz_ert.plugins import WebvizErtPluginABC

from dash import html
from dash import dcc
import webviz_core_components as wcc
import dash_bootstrap_components as dbc


def parameter_selector_view(
    parent: WebvizErtPluginABC, data_type: str = "parameter", suffix: str = ""
) -> Component:
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.Label(
                            "Search",
                            className="ert-label",
                        ),
                        align="left",
                        width="auto",
                    ),
                    dbc.Col(
                        dcc.Input(
                            id=parent.uuid(f"parameter-selector-filter-{suffix}"),
                            type="search",
                            placeholder="Substring...",
                            persistence="session",
                        ),
                        align="left",
                    ),
                    dbc.Col(
                        html.Button(
                            id=parent.uuid(f"parameter-selector-button-{suffix}"),
                            children=("Toggle selector visibility"),
                        ),
                        align="right",
                    ),
                ],
            ),
            html.Div(
                wcc.Select(
                    id=parent.uuid(f"parameter-selector-multi-{suffix}"),
                    multi=True,
                    size=10,
                    persistence="session",
                ),
                id=parent.uuid(f"container-parameter-selector-multi-{suffix}"),
                className="ert-parameter-selector-container-show",
            ),
            dcc.Dropdown(
                id=parent.uuid(f"parameter-deactivator-{suffix}"),
                multi=True,
                searchable=False,
                placeholder="",
                persistence="session",
            ),
            dcc.Store(
                id=parent.uuid(f"parameter-selection-store-{suffix}"),
                storage_type="session",
                data=parent.load_state(f"parameter-selection-store-{suffix}", []),
            ),
            dcc.Store(
                id=parent.uuid(f"parameter-type-store-{suffix}"),
                storage_type="session",
                data=data_type,
            ),
        ],
    )
