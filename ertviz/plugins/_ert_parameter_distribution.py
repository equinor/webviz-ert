import dash
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_core_components as dcc
from webviz_config import WebvizPluginABC
import webviz_subsurface_components as wsc

from .._data_input.common_requests import get_data, get_ensembles, api_request


def get_parameter_options(ensembles):
    parameter_options = list()
    used_keys = set()
    for ensemble in ensembles:
        for param in api_request(ensemble["ref_url"])["parameters"]:
            if param["key"] not in used_keys:
                parameter_options.append({"label": param["key"], "value": param["key"]})
                used_keys.add(param["key"])
    return parameter_options


def set_grid_layout(columns):
    return {
        "display": "grid",
        "alignContent": "space-around",
        "justifyContent": "space-between",
        "gridTemplateColumns": f"{columns}",
    }


def make_buttons(prev_id, next_id):
    return html.Div(
        style=set_grid_layout("1fr 1fr"),
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


def prev_value(current_value, options):
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


def get_parameter_data(ensemble_schema, parameter):
    realization_names = list()
    realization_parameters = list()

    for parameter_dict in ensemble_schema["parameters"]:
        if parameter == parameter_dict["key"]:
            ref_url = parameter_dict["ref_url"]

    for realization in api_request(ref_url)["parameter_realizations"]:
        realization_names.append(realization["name"])
        realization_parameters.extend(get_data(realization["data_url"]))

    return (realization_names, realization_parameters)


class ERTParameterDistribution(WebvizPluginABC):
    def __init__(self, app):

        super().__init__()

        self.set_callbacks(app)

        self.ensembles = get_ensembles()
        self.parameter_options = get_parameter_options(self.ensembles)

    @property
    def layout(self):
        return html.Div(
            children=[
                html.Span("Parameter distribution:", style={"font-weight": "bold"}),
                html.Div(
                    style=set_grid_layout("8fr 1fr 2fr"),
                    children=[
                        dcc.Dropdown(
                            id="parameter-selector",
                            options=self.parameter_options,
                            value=self.parameter_options[0]["value"],
                            clearable=False,
                        ),
                        make_buttons("prev-btn", "next-btn"),
                    ],
                ),
                wsc.PriorPosteriorDistribution(
                    "parameter-graph",
                    data={"iterations": [[]], "values": [[]], "labels": []},
                ),
            ],
        )

    def set_callbacks(self, app):
        @app.callback(
            Output("parameter-graph", "data"), [Input("parameter-selector", "value")]
        )
        def _set_parameter(parameter):
            iterations = []
            values = []
            labels = []

            for ensemble in self.ensembles:
                ensemble_schema = api_request(ensemble["ref_url"])
                (realizations, params) = get_parameter_data(ensemble_schema, parameter)
                if realizations:
                    iterations.append(ensemble_schema["name"])
                    values.append(params)
                    labels.append([f"Realization {real}" for real in realizations])
            return {"iterations": iterations, "values": values, "labels": labels}

        @app.callback(
            Output("parameter-selector", "value"),
            [Input("prev-btn", "n_clicks"), Input("next-btn", "n_clicks"),],
            [State("parameter-selector", "value"),],
        )
        def _set_parameter_from_btn(_prev_click, _next_click, parameter):
            ctx = dash.callback_context.triggered
            if not ctx:
                raise PreventUpdate

            callback = ctx[0]["prop_id"]
            if callback == f"{'prev-btn'}.n_clicks":
                parameter = prev_value(
                    parameter, [option["value"] for option in self.parameter_options]
                )
            elif callback == f"{'next-btn'}.n_clicks":
                parameter = next_value(
                    parameter, [option["value"] for option in self.parameter_options]
                )
            return parameter
