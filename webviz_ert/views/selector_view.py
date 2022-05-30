from dash.development.base_component import Component
from webviz_ert.plugins import WebvizErtPluginABC

from dash import html
from dash import dcc
import webviz_core_components as wcc
import dash_bootstrap_components as dbc

from webviz_ert.models.data_model import DataType


def parameter_selector_view(
    parent: WebvizErtPluginABC,
    data_type: DataType,
    titleLabel: str = "Parameters",
) -> Component:
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.H6(
                            titleLabel,
                            className="ert-label",
                        ),
                        align="left",
                    ),
                    dbc.Col(
                        [
                            html.Label(
                                "Search: ",
                                className="ert-label",
                            ),
                            dcc.Input(
                                id=parent.uuid(
                                    f"parameter-selector-filter-{data_type}"
                                ),
                                type="search",
                                placeholder="Substring...",
                                persistence="session",
                            ),
                        ],
                        align="right",
                        width="auto",
                    ),
                ],
                align="center",
            ),
            html.Div(
                wcc.Select(
                    id=parent.uuid(f"parameter-selector-multi-{data_type}"),
                    multi=True,
                    size=10,
                    persistence="session",
                ),
                id=parent.uuid(f"container-parameter-selector-multi-{data_type}"),
                className="ert-parameter-selector-container-show",
            ),
            dcc.Dropdown(
                id=parent.uuid(f"parameter-deactivator-{data_type}"),
                multi=True,
                searchable=False,
                placeholder="",
                persistence="session",
            ),
            dcc.Store(
                id=parent.uuid(f"parameter-selection-store-{data_type}"),
                storage_type="session",
                data=parent.load_state(f"{data_type}", []),
            ),
        ],
    )
