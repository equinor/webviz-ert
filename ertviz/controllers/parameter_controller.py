import re
import dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import plotly.express as px
from ertviz.controllers import parse_url_query
from ertviz.data_loader import get_ensembles


def _prev_value(current_value, options):
    try:
        index = options.index(current_value)
    except ValueError:
        index = None
    if index > 0:
        return options[index - 1]
    return current_value


def next_value(current_value, options):
    try:
        index = options.index(current_value)
    except ValueError:
        index = None
    if index < len(options) - 1:
        return options[index + 1]
    return current_value


def parameter_controller(parent, app):
    @app.callback(
        Output(parent.uuid("parameter-selector"), "options"), [Input("url", "search")]
    )
    def update_parameter_options(search):
        queries = parse_url_query(search)
        if not "ensemble_id" in queries:
            return []
        ensemble_id = queries["ensemble_id"]
        return [
            {"label": parameter_key, "value": (ensemble_id, parameter_key)}
            for parameter_key in get_ensembles(ensemble_id).parameters.key
        ]

    @app.callback(
        Output(
            {"id": parent.uuid("parameter-scatter"), "type": parent.uuid("graph")},
            "figure",
        ),
        [
            Input(parent.uuid("parameter-selector"), "value"),
            Input(parent.uuid("selection-store"), "data"),
        ],
    )
    def _update_scatter_plot(parameter_idx, selection):
        ens_id, param_key = parameter_idx

        if not param_key in get_ensembles(ens_id).parameters.key:
            raise PreventUpdate

        data_frame = get_ensembles(ens_id).parameters[param_key].data
        if selection is not None:
            data_frame = data_frame.loc[selection]
        fig = px.histogram(data_frame, marginal="rug")
        fig.update_layout(clickmode="event+select")

        fig.update_layout(uirevision=True)
        return fig

    @app.callback(
        Output(parent.uuid("parameter-selector"), "value"),
        [
            Input(parent.uuid("prev-btn"), "n_clicks"),
            Input(parent.uuid("next-btn"), "n_clicks"),
            Input(parent.uuid("parameter-selector"), "options"),
        ],
        [State(parent.uuid("parameter-selector"), "value")],
    )
    def _set_parameter_from_btn(_prev_click, _next_click, parameter_options, parameter):

        ctx = dash.callback_context.triggered

        callback = ctx[0]["prop_id"]
        if callback == f"{parent.uuid('prev-btn')}.n_clicks":
            parameter = _prev_value(
                parameter, [option["value"] for option in parameter_options]
            )
        elif callback == f"{parent.uuid('next-btn')}.n_clicks":
            parameter = next_value(
                parameter, [option["value"] for option in parameter_options]
            )
        elif parameter_options:
            parameter = parameter_options[0]["value"]
        else:
            raise PreventUpdate
        return parameter
