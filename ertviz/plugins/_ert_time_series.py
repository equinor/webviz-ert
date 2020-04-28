from datetime import datetime

import requests
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
from webviz_config import WebvizPluginABC

from .._data_input.common_requests import get_data, get_ensembles, api_request


def convertdate(dstring):
    return datetime.strptime(dstring, "%Y-%m-%d %H:%M:%S")


def get_axis(data_url):
    indexes = requests.get(data_url).text.split(",")
    if indexes and ":" in indexes[0]:
        return list(map(convertdate, indexes))
    return list(map(int, indexes))


def get_realizations_data(realizations, x_axis):
    realizations_data = list()
    for realization in realizations:
        data = get_data(realization["data_url"])
        realization_data = dict(
            x=x_axis,
            y=data,
            text="Realization {}".format(realization["name"]),
            name="Realization {}".format(realization["name"]),
            mode="line",
            line=dict(color="royalblue"),
        )
        realizations_data.append(realization_data)
    return realizations_data


def get_observation_data(observation, x_axis):
    data = get_data(observation["values"]["data_url"])
    stds = get_data(observation["std"]["data_url"])
    x_axis_indexes = get_axis(observation["data_indexes"]["data_url"])
    x_axis = [x_axis[i] for i in x_axis_indexes]
    observation_data = dict(
        x=x_axis,
        y=data,
        text="Observations",
        name="Observations",
        mode="markers",
        marker=dict(color="red", size=10),
    )
    lower_std_data = dict(
        x=x_axis,
        y=[d - std for d, std in zip(data, stds)],
        text="Observations std lower",
        name="Observations std lower",
        mode="line",
        line=dict(color="red", dash="dash"),
    )
    upper_std_data = dict(
        x=x_axis,
        y=[d + std for d, std in zip(data, stds)],
        text="Observations std upper",
        name="Observations std upper",
        mode="line",
        line=dict(color="red", dash="dash"),
    )
    return [observation_data, lower_std_data, upper_std_data]


class ERTTimeSeries(WebvizPluginABC):
    def __init__(self, app):
        super().__init__()
        self.set_callbacks(app)
        self.ensembles = get_ensembles()

    @property
    def layout(self):
        return html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.H5("Ensemble"),
                                dcc.Dropdown(
                                    id=self.uuid("ensemble-selector"),
                                    options=[
                                        {
                                            "label": ensemble["name"],
                                            "value": ensemble["ref_url"],
                                        }
                                        for ensemble in self.ensembles
                                    ],
                                    value=self.ensembles[0]["ref_url"],
                                ),
                            ],
                            style={"width": "48%", "display": "inline-block"},
                        ),
                        html.Div(
                            [
                                html.H5("Response"),
                                dcc.Dropdown(id=self.uuid("response-selector")),
                            ],
                            style={
                                "width": "48%",
                                "float": "right",
                                "display": "inline-block",
                            },
                        ),
                    ]
                ),
                dcc.Graph(id=self.uuid("responses-graphic")),
            ]
        )

    def set_callbacks(self, app):
        @app.callback(
            Output(self.uuid("response-selector"), "options"),
            [Input(self.uuid("ensemble-selector"), "value")],
        )
        def _set_response_options(selected_ensemble_id):
            ensemble_schema = api_request(selected_ensemble_id)
            return [
                {"label": response["name"], "value": response["ref_url"]}
                for response in ensemble_schema["responses"]
            ]

        @app.callback(
            Output(self.uuid("response-selector"), "value"),
            [Input(self.uuid("response-selector"), "options")],
        )
        def _set_responses_value(available_options):
            return available_options[0]["value"]

        @app.callback(
            Output(self.uuid("responses-graphic"), "figure"),
            [Input(self.uuid("response-selector"), "value"),],
        )
        def _update_graph(yaxis_column_name):
            response = api_request(yaxis_column_name)
            x_axis = get_axis(response["axis"]["data_url"])
            plot_lines = get_realizations_data(response["realizations"], x_axis)
            if "observation" in response:
                plot_lines += get_observation_data(
                    response["observation"]["data"], x_axis
                )
            return {
                "data": plot_lines,
                "layout": dict(
                    xaxis={"title": "Index",},
                    yaxis={"title": "Unit TODO",},
                    margin={"l": 40, "b": 40, "t": 10, "r": 0},
                    hovermode="closest",
                ),
            }
