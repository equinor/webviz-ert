import dash
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State, ALL, MATCH
from dash.exceptions import PreventUpdate
from ertviz.models import ResponsePlotModel, PlotModel, EnsembleModel, load_ensemble
import ertviz.assets as assets


def _get_realizations_plots(realizations_df, x_axis, color):
    style = assets.ERTSTYLE["response-plot"]["response"].copy()
    style.update({"line": {"color": color}})
    realizations_data = list()
    for realization in realizations_df:
        plot = PlotModel(
            x_axis=x_axis,
            y_axis=realizations_df[realization].values,
            text=realization,
            name=realization,
            **style
        )
        realizations_data.append(plot)
    return realizations_data


def _get_realizations_statistics_plots(df_response, x_axis, color):
    data = df_response
    p10 = data.quantile(0.1, axis=1)
    p90 = data.quantile(0.9, axis=1)
    _mean = data.mean(axis=1)
    style = assets.ERTSTYLE["response-plot"]["statistics"].copy()
    style.update({"line": {"color": color}})
    mean_data = PlotModel(
        x_axis=x_axis, y_axis=_mean, text="Mean", name="Mean", **style
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

    observation_data = PlotModel(
        x_axis=x_axis,
        y_axis=data,
        text="Observations",
        name="Observations",
        error_y=dict(
            type="data",  # value of error bar given in data coordinates
            array=stds.values,
            visible=True,
        ),
        **assets.ERTSTYLE["response-plot"]["observation"]
    )
    return [observation_data]


def _create_response_plot(response, plot_type, selected_realizations, color):

    x_axis = response.axis
    if plot_type == "Statistics":
        realizations = _get_realizations_statistics_plots(
            response.data_df(selected_realizations), x_axis, color=color
        )
    else:
        realizations = _get_realizations_plots(
            response.data_df(selected_realizations), x_axis, color=color
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


def _valid_response_option(response_filters, response):
    if "obs" in response_filters:
        return response.observations
    else:
        return True


def multi_response_controller(parent, app):
    @app.callback(
        Output({"index": ALL, "type": parent.uuid("response-selector")}, "options"),
        [
            Input(parent.uuid("ensemble-selection-store"), "data"),
            Input(parent.uuid("response-observations-check"), "value"),
        ],
        [State({"index": ALL, "type": parent.uuid("response-selector")}, "options")],
    )
    def _set_response_options(selected_ensembles, response_filters, selectors):
        # Should either return a union of all possible responses or the other thing which I cant think of...
        if not selected_ensembles:
            raise PreventUpdate
        ensemble_id, _ = selected_ensembles.popitem()
        ensemble = load_ensemble(parent, ensemble_id)
        return [
            [
                {
                    "label": response,
                    "value": response,
                }
                for response in ensemble.responses
                if _valid_response_option(
                    response_filters, ensemble.responses[response]
                )
            ]
            for i in range(len(selectors))
        ]

    @app.callback(
        Output({"index": MATCH, "type": parent.uuid("response-selector")}, "value"),
        [Input({"index": MATCH, "type": parent.uuid("response-selector")}, "options")],
        [State({"index": MATCH, "type": parent.uuid("response-selector")}, "value")],
    )
    def _set_responses_value(available_options, previous_selected_response):
        if available_options and previous_selected_response in [
            opt["value"] for opt in available_options
        ]:
            return previous_selected_response
        if available_options and not previous_selected_response:
            return available_options[0]["value"]
        return ""

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
            Input({"index": MATCH, "type": parent.uuid("response-selector")}, "value"),
            Input({"index": MATCH, "type": parent.uuid("plot-type")}, "value"),
        ],
        [State(parent.uuid("ensemble-selection-store"), "data")],
    )
    def _update_graph(response, plot_type, selected_ensembles):
        if response in [None, ""] or not selected_ensembles:
            raise PreventUpdate

        def _generate_plot(ensemble_id, color):
            ensemble = load_ensemble(parent, ensemble_id)
            plot = _create_response_plot(
                ensemble.responses[response], plot_type, None, color
            )
            return plot

        response_plots = [
            _generate_plot(ensemble_id, data["color"])
            for ensemble_id, data in selected_ensembles.items()
        ]

        fig = go.Figure()
        for plot in response_plots:
            for trace in plot.repr.data:
                fig.add_trace(trace)
        fig.update_layout(assets.ERTSTYLE["figure"]["layout"])
        return fig
