import dash
import json
import pandas as pd
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from ertviz.data_loader import get_ensemble_url
from ertviz.models import ResponsePlotModel, PlotModel, EnsembleModel
from ertviz.controllers import parse_url_query
import ertviz.assets as assets


def _get_realizations_plots(realizations_df, x_axis):
    realizations_data = list()
    for realization in realizations_df:
        plot = PlotModel(
            x_axis=x_axis,
            y_axis=realizations_df[realization].values,
            text=realization,
            name=realization,
            **assets.ERTSTYLE["response-plot"]["response"]
        )
        realizations_data.append(plot)
    return realizations_data


def _get_realizations_statistics_plots(df_response, x_axis):
    data = df_response
    p10 = data.quantile(0.1, axis=1)
    p90 = data.quantile(0.9, axis=1)
    _mean = data.mean(axis=1)
    mean_data = PlotModel(
        x_axis=x_axis,
        y_axis=_mean,
        text="Mean",
        name="Mean",
        **assets.ERTSTYLE["response-plot"]["statistics"]
    )
    lower_std_data = PlotModel(
        x_axis=x_axis,
        y_axis=p10,
        text="p10 quantile",
        name="p10 quantile",
        **assets.ERTSTYLE["response-plot"]["statistics"]
    )
    upper_std_data = PlotModel(
        x_axis=x_axis,
        y_axis=p90,
        text="p90 quantile",
        name="p90 quantile",
        **assets.ERTSTYLE["response-plot"]["statistics"]
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


def _create_response_plot(response, plot_type, selected_realizations):

    x_axis = response.axis
    if plot_type == "Statistics":
        realizations = _get_realizations_statistics_plots(
            response.data_df(selected_realizations), x_axis
        )
    else:
        realizations = _get_realizations_plots(
            response.data_df(selected_realizations), x_axis
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
        ensemble = parent.ensembles.get(
            ensemble_id, EnsembleModel(ref_url=get_ensemble_url(ensemble_id))
        )
        parent.ensembles[ensemble_id] = ensemble
        return [
            {
                "label": response,
                # Dash does only allow string/string pairs for dropdowns
                # using json to encode more values
                "value": json.dumps({"response": response, "ensemble_id": ensemble_id}),
            }
            for response in ensemble.responses
        ]

    @app.callback(
        Output(parent.uuid("response-selector"), "value"),
        [Input(parent.uuid("response-selector"), "options")],
    )
    def _set_responses_value(available_options):
        if available_options:
            return available_options[0]["value"]
        return ""

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
    def _update_graph(value, selected_realizations, plot_type):

        if value is not None and value is not "":
            value = json.loads(value)
        if value in [None, ""] and parent.ensemble_plot is None:
            raise PreventUpdate
        ctx = dash.callback_context

        if not ctx.triggered:
            raise PreventUpdate
        else:
            select_update = ctx.triggered[0]["prop_id"].split(".")[0] == parent.uuid(
                "selection-store"
            )

        def _update_plot(ensemble_id):
            ensemble = parent.ensembles.get(ensemble_id, None)
            parent.ensemble_plot = _create_response_plot(
                ensemble.responses[value["response"]],
                plot_type,
                selected_realizations,
            )

        if select_update:
            parent.ensemble_plot.selection = selected_realizations
        else:
            ensemble_id = value["ensemble_id"]
            _update_plot(ensemble_id)

        return parent.ensemble_plot.repr
