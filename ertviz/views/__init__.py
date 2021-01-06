import dash_html_components as html
import dash_core_components as dcc
import webviz_core_components as wcc
from .paremeter_view import parameter_view
from .ensemble_selector_view import ensemble_selector_view
from .response_view import response_view
from .plot_view import plot_view_body, plot_view_header
from .misfit_view import response_obs_view
from .paralell_coordinates_view import paralell_coordinates_view


def parameter_selector_view(parent):
    return html.Div(
        children=[
            html.Div(
                [
                    html.Label("Search substring:"),
                    dcc.Input(
                        id=parent.uuid("parameter-selector-filter"),
                        type="search",
                        placeholder="",
                    ),
                ],
            ),
            wcc.Select(
                id=parent.uuid("parameter-selector-multi"),
                multi=True,
                size=10,
                persistence=True,
                persistence_type="session",
                className="ert-dropdown",
            ),
        ],
    )