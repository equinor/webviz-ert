import dash_html_components as html
import dash_core_components as dcc
import webviz_core_components as wcc
import dash_bootstrap_components as dbc


def parameter_selector_view(parent, data_type="parameter"):
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.Label("Search:", className="ert-label"),
                        align="left",
                        width="auto",
                    ),
                    dbc.Col(
                        dcc.Input(
                            id=parent.uuid("parameter-selector-filter"),
                            type="search",
                            placeholder="Substring...",
                            persistence="session",
                        ),
                        align="left",
                    ),
                ],
            ),
            wcc.Select(
                id=parent.uuid("parameter-selector-multi"),
                multi=True,
                size=10,
                persistence="session",
                className="ert-dropdown",
            ),
            dcc.Dropdown(
                id=parent.uuid("parameter-deactivator"),
                multi=True,
                persistence="session",
            ),
            dcc.Store(
                id=parent.uuid("parameter-selection-store"), storage_type="session"
            ),
            dcc.Store(
                id=parent.uuid("parameter-type-store"),
                storage_type="session",
                data=data_type,
            ),
        ],
    )
