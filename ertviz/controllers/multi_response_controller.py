import dash
import plotly.graph_objects as go
from copy import deepcopy
from dash.dependencies import Input, Output, State, ALL, MATCH
from dash.exceptions import PreventUpdate
from ertviz.models import ResponsePlotModel, PlotModel, EnsembleModel, load_ensemble
from ertviz.controllers.controller_functions import response_options
import ertviz.assets as assets


def _get_realizations_plots(realizations_df, x_axis, color, style=None):
    if not style:
        style = assets.ERTSTYLE["response-plot"]["response"].copy()
    style.update({"line": {"color": color}})
    style.update({"marker": {"color": color}})
    realizations_data = list()
    for realization in realizations_df:
        plot = PlotModel(
            x_axis=x_axis,
            y_axis=realizations_df[realization].values,
            text=realization,
            name=realization,
            **style,
        )
        realizations_data.append(plot)
    return realizations_data


def _get_realizations_statistics_plots(df_response, x_axis, color):
    data = df_response
    p10 = data.quantile(0.1, axis=1)
    p90 = data.quantile(0.9, axis=1)
    _mean = data.mean(axis=1)
    style = deepcopy(assets.ERTSTYLE["response-plot"]["statistics"])
    style["line"]["color"] = color
    style_mean = deepcopy(style)
    style_mean["line"]["dash"] = "solid"
    mean_data = PlotModel(
        x_axis=x_axis, y_axis=_mean, text="Mean", name="Mean", **style_mean
    )
    lower_std_data = PlotModel(
        x_axis=x_axis, y_axis=p10, text="p10 quantile", name="p10 quantile", **style
    )
    upper_std_data = PlotModel(
        x_axis=x_axis, y_axis=p90, text="p90 quantile", name="p90 quantile", **style
    )
    return [mean_data, lower_std_data, upper_std_data]


def _get_observation_plots(observation_df, x_axis):
    data = observation_df["values"]
    stds = observation_df["std"]
    x_axis = observation_df["x_axis"]
    attributes = observation_df["attributes"]
    active_mask = observation_df["active"]

    style = assets.ERTSTYLE["response-plot"]["observation"]
    color = [style["color"] if active else "rgb(0, 0, 0)" for active in active_mask]
    style["marker"]["color"] = color

    observation_data = PlotModel(
        x_axis=x_axis,
        y_axis=data,
        text=attributes,
        name="Observation",
        error_y=dict(
            type="data",  # value of error bar given in data coordinates
            array=stds.values,
            visible=True,
        ),
        **style,
    )
    return [observation_data]


def _create_response_plot(
    response, plot_type, selected_realizations, color, style=None
):

    x_axis = response.axis
    if plot_type == "Statistics":
        realizations = _get_realizations_statistics_plots(
            response.data_df(selected_realizations), x_axis, color=color
        )
    else:
        realizations = _get_realizations_plots(
            response.data_df(selected_realizations), x_axis, color=color, style=style
        )
    observations = []

    for obs in response.observations:
        observations += _get_observation_plots(obs.data_df(), x_axis)

    ensemble_plot = ResponsePlotModel(
        realizations,
        observations,
        dict(
            xaxis={"title": "Index"},
            yaxis={"title": "Unit TODO"},
        ),
    )
    return ensemble_plot


def multi_response_controller(parent, app):
    @app.callback(
        Output(
            {
                "index": MATCH,
                "id": parent.uuid("response-graphic"),
                "type": parent.uuid("graph"),
            },
            "figure",
        ),
        [
            Input({"index": MATCH, "type": parent.uuid("plot-type")}, "value"),
            Input(parent.uuid("ensemble-selection-store"), "modified_timestamp"),
        ],
        [
            State(parent.uuid("ensemble-selection-store"), "data"),
            State({"index": MATCH, "type": parent.uuid("response-id-store")}, "data"),
        ],
    )
    def update_graph(plot_type, _, selected_ensembles, response):
        if response in [None, ""] or not selected_ensembles:
            raise PreventUpdate

        def _generate_plot(ensemble_id, color):
            ensemble = load_ensemble(parent, ensemble_id)
            if response not in ensemble.responses:
                return None
            plot = _create_response_plot(
                ensemble.responses[response], plot_type, None, color
            )
            return plot

        response_plots = [
            _generate_plot(ensemble_id, data["color"])
            for ensemble_id, data in selected_ensembles.items()
        ]

        fig = go.Figure()
        for plot in filter(None, response_plots):
            for realization in plot._realization_plots:
                fig.add_trace(realization.repr)
        for plot in filter(None, response_plots):
            for observation in plot._observations:
                fig.add_trace(observation.repr)
        fig.update_layout(assets.ERTSTYLE["figure"]["layout"])
        return fig
