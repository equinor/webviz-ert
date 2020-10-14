import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from ertviz.data_loader import get_ensembles
from ertviz.models import EnsemblePlotModel, PlotModel
from ertviz.controllers import parse_url_query

obs_color = "rgb(180, 180, 180)"
real_color = "rgb(40, 141, 181)"


def _get_realizations_data(response, x_axis):
    realizations_data = list()
    for realization in response.realizations:
        plot = PlotModel(
            x_axis=x_axis,
            y_axis=realization.data,
            text=realization.name,
            name=realization.name,
            mode="line",
            line=dict(color=real_color),
            marker=None,
        )
        realizations_data.append(plot)
    return realizations_data


def _get_realizations_statistics_data(response, x_axis):
    data = response.data
    _std = data.std(axis=0)
    _mean = data.mean(axis=0)
    mean_data = PlotModel(
        x_axis=x_axis,
        y_axis=_mean,
        text="Mean",
        name="Mean",
        mode="line",
        line=dict(color=real_color, dash="dash"),
        marker=None,
    )
    lower_std_data = PlotModel(
        x_axis=x_axis,
        y_axis=_mean - _std,
        text="Realizations std lower",
        name="Realizations std lower",
        mode="line",
        line=dict(color=real_color, dash="dash"),
        marker=None,
    )
    upper_std_data = PlotModel(
        x_axis=x_axis,
        y_axis=_mean + _std,
        text="Realizations std upper",
        name="Realizations std upper",
        mode="line",
        line=dict(color=real_color, dash="dash"),
        marker=None,
    )

    return [mean_data, lower_std_data, upper_std_data]


def _get_observation_data(observation, x_axis):
    data = observation.values.data
    stds = observation.std.data
    x_axis_indexes = observation.data_indexes.data_as_axis
    x_axis = [x_axis[i] for i in x_axis_indexes]
    observation_data = PlotModel(
        x_axis=x_axis,
        y_axis=data,
        text="Observations",
        name="Observations",
        mode="markers",
        line=None,
        marker=dict(color=obs_color, size=10),
    )
    lower_std_data = PlotModel(
        x_axis=x_axis,
        y_axis=[d - std for d, std in zip(data, stds)],
        text="Observations std lower",
        name="Observations std lower",
        mode="line",
        line=dict(color=obs_color, dash="dash"),
        marker=None,
    )
    upper_std_data = PlotModel(
        x_axis=x_axis,
        y_axis=[d + std for d, std in zip(data, stds)],
        text="Observations std upper",
        name="Observations std upper",
        mode="line",
        line=dict(color=obs_color, dash="dash"),
        marker=None,
    )
    return [observation_data, lower_std_data, upper_std_data]


def _create_response_model(response, plot_type):
    x_axis = response.axis.data
    if plot_type == "Statistics":
        realizations = _get_realizations_statistics_data(response, x_axis)
    else:
        realizations = _get_realizations_data(response, x_axis)
    observations = []

    for obs in response.observations:
        observations += _get_observation_data(obs, x_axis)

    ensemble_plot = EnsemblePlotModel(
        realizations,
        observations,
        dict(
            xaxis={"title": "Index"},
            yaxis={"title": "Unit TODO"},
            margin={"l": 40, "b": 40, "t": 10, "r": 0},
            hovermode="closest",
            uirevision=True,
        ),
    )
    return ensemble_plot


def response_controller(parent, app):
    @app.callback(
        Output(parent.uuid("response-selector"), "options"), [Input("url", "search")]
    )
    def _set_response_options(query):
        queries = parse_url_query(query)
        if not "ensemble_id" in queries:
            return []
        ensemble_id = queries["ensemble_id"]
        return [
            {"label": name, "value": (ensemble_id, name)}
            for name in get_ensembles(ensemble_id).responses.name
        ]

    @app.callback(
        Output(parent.uuid("response-selector"), "value"),
        [Input(parent.uuid("response-selector"), "options")],
    )
    def _set_responses_value(available_options):
        print(available_options)
        if available_options:
            return available_options[0]["value"]
        return None

    @app.callback(
        Output(
            {"id": parent.uuid("response-graphic"), "type": parent.uuid("graph")},
            "figure",
        ),
        [
            Input(parent.uuid("response-selector"), "value"),
            Input(parent.uuid("selection-store"), "data"),
            Input(parent.uuid("plot-type"), "value"),
        ],
    )
    def _update_graph(response_idx, selected_realizations, plot_type):

        # if response_url in [None, ""] and parent.ensemble_plot is None:
        #     raise PreventUpdate
        print(plot_type)
        if response_idx in [None, ""]:
            raise PreventUpdate
        ctx = dash.callback_context

        if not ctx.triggered:
            raise PreventUpdate
        else:
            select_update = ctx.triggered[0]["prop_id"].split(".")[0] == parent.uuid(
                "selection-store"
            )

        if select_update:
            parent.ensemble_plot.selection = selected_realizations
        else:
            print(response_idx)
            ens_id, res_id = response_idx
            parent.ensemble_plot = _create_response_model(
                get_ensembles(ens_id).responses[res_id], plot_type
            )
        return parent.ensemble_plot.repr
