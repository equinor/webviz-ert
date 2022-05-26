from dash.development.base_component import Component
from webviz_config import WebvizPluginABC

from dash import html
from dash import dcc
from webviz_ert.models.data_model import DataType


def element_dropdown_view(parent: WebvizPluginABC, data_type: DataType) -> Component:
    return html.Div(
        [
            dcc.Dropdown(
                id=parent.uuid(f"element-dropdown-{data_type}"),
                multi=False,
            ),
            dcc.Store(
                id=parent.uuid(f"element-dropdown-store-{data_type}"),
                storage_type="session",
                data=None,
            ),
        ],
    )
