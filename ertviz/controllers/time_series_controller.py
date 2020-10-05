from datetime import datetime
from dash.dependencies import Input, Output
from ertviz.data_loader import RequestHandler, DataLoader
from ertviz.models.time_series_model import EnsemblePlotModel, PlotModel

request_handler = RequestHandler(base_url="http://127.0.0.1:5000")
data_loader = DataLoader(request_handler=request_handler)


def _convertdate(dstring):
    return datetime.strptime(dstring, "%Y-%m-%d %H:%M:%S")


def _get_axis(data_url):
    indexes = data_loader.get_data(data_url)
    if indexes and ":" in indexes[0]:
        return list(map(_convertdate, indexes))
    return list(map(int, indexes))


def _get_realizations_data(realizations, x_axis):
    realizations_data = list()
    for realization in realizations:
        data = data_loader.get_data(realization["data_url"])
        plot = PlotModel(
            x_axis=x_axis,
            y_axis=data,
            text="Realization {}".format(realization["name"]),
            name="Realization {}".format(realization["name"]),
            mode="line",
            line=dict(color="royalblue"),
            marker=None,
        )
        realizations_data.append(plot)
    return realizations_data


def _get_observation_data(observation, x_axis):
    data = data_loader.get_data(observation["values"]["data_url"])
    stds = data_loader.get_data(observation["std"]["data_url"])
    x_axis_indexes = _get_axis(observation["data_indexes"]["data_url"])
    x_axis = [x_axis[i] for i in x_axis_indexes]
    observation_data = PlotModel(
        x_axis=x_axis,
        y_axis=data,
        text="Observations",
        name="Observations",
        mode="markers",
        line=None,
        marker=dict(color="red", size=10),
    )
    lower_std_data = PlotModel(
        x_axis=x_axis,
        y_axis=[d - std for d, std in zip(data, stds)],
        text="Observations std lower",
        name="Observations std lower",
        mode="line",
        line=dict(color="red", dash="dash"),
        marker=None,
    )
    upper_std_data = PlotModel(
        x_axis=x_axis,
        y_axis=[d + std for d, std in zip(data, stds)],
        text="Observations std upper",
        name="Observations std upper",
        mode="line",
        line=dict(color="red", dash="dash"),
        marker=None,
    )
    return observation_data + lower_std_data + upper_std_data


def timeseries_controller(parent, app):
    @app.callback(
        Output(parent.uuid("response-selector"), "options"), [Input("url", "pathname")]
    )
    def _set_response_options(pathname):
        ensemble_id = pathname.strip("/")
        ensemble_schema = data_loader.get_ensemble(ensemble_id)
        if "responses" in ensemble_schema:
            return [
                {"label": response["name"], "value": response["ref_url"]}
                for response in ensemble_schema["responses"]
            ]
        return []

    @app.callback(
        Output(parent.uuid("response-selector"), "value"),
        [Input(parent.uuid("response-selector"), "options")],
    )
    def _set_responses_value(available_options):
        if available_options:
            return available_options[0]["value"]
        return ""

    @app.callback(
        Output(parent.uuid("responses-graphic"), "figure"),
        [
            Input(parent.uuid("response-selector"), "value"),
        ],
    )
    def _update_graph(value):
        if value is None or value == "":
            return EnsemblePlotModel(
                [],
                [],
                dict(
                    xaxis={
                        "title": "Index",
                    },
                    yaxis={
                        "title": "Unit TODO",
                    },
                    margin={"l": 40, "b": 40, "t": 10, "r": 0},
                    hovermode="closest",
                ),
            ).repr

        response = data_loader.get_schema(value)
        x_axis = _get_axis(response["axis"]["data_url"])
        realizations = _get_realizations_data(response["realizations"], x_axis)
        observations = []
        if "observation" in response:
            observations = _get_observation_data(
                response["observation"]["data"], x_axis
            )
        ensemble_plot = EnsemblePlotModel(
            realizations,
            observations,
            dict(
                xaxis={
                    "title": "Index",
                },
                yaxis={
                    "title": "Unit TODO",
                },
                margin={"l": 40, "b": 40, "t": 10, "r": 0},
                hovermode="closest",
            ),
        )
        return ensemble_plot.repr
