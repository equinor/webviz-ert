import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from copy import deepcopy
from ertviz.models import ResponsePlotModel, BoxPlotModel, PlotModel, EnsembleModel
import ertviz.assets as assets


def _get_univariate_misfits_plots(misfits_df, color):
    if misfits_df is None:
        return []
    style = deepcopy(assets.ERTSTYLE["observation-response-plot"]["misfits"])
    style["line"]["color"] = color
    style["marker"]["color"] = color
    x_axis = misfits_df.pop("x_axis")
    misfits_data = list()
    for misfits in misfits_df:
        plot = PlotModel(
            x_axis=x_axis,
            y_axis=misfits_df[misfits].pow(1 / 2.0).values,
            text=misfits,
            name=misfits,
            **style,
        )
        misfits_data.append(plot)
    return misfits_data


def _get_univariate_misfits_boxplots(misfits_df, color):
    if misfits_df is None:
        return []
    x_axis = misfits_df.pop("x_axis")
    misfits_data = list()
    for misfits in misfits_df.T:
        plot = BoxPlotModel(
            x_axis=[x_axis.loc[misfits]],
            y_axis=misfits_df.T[misfits].pow(1 / 2.0).values,
            text=misfits,
            name=f"Misfits@{int(x_axis.loc[misfits])}",
            color=color,
        )
        misfits_data.append(plot)
    return misfits_data


def _get_observation_plots(observation_df, x_axis):
    data = observation_df["values"]
    stds = observation_df["std"]
    x_axis = observation_df["x_axis"]
    style = deepcopy(assets.ERTSTYLE["observation-response-plot"]["observation"])
    observation_data = PlotModel(
        x_axis=x_axis,
        y_axis=stds.values,
        text="Observations",
        name="Observations",
        **style,
    )
    return [observation_data]


def _create_misfits_plot(response, yaxis_type, selected_realizations, color):

    x_axis = response.axis
    # realizations = _get_univariate_misfits_plots(
    realizations = _get_univariate_misfits_boxplots(
        response.univariate_misfits_df(selected_realizations), color=color
    )
    observations = []

    # for obs in response.observations:
    #     observations += _get_observation_plots(obs.data_df(), x_axis)

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


def observation_response_controller(parent, app):
    @app.callback(
        Output(parent.uuid("response-selector"), "options"),
        [Input(parent.uuid("ensemble-selection-store"), "data")],
    )
    def _set_response_options(selected_ensembles):
        # Should either return a union of all possible responses or the other thing which I cant think of...

        if not selected_ensembles:
            raise PreventUpdate
        ensemble_id, _ = selected_ensembles.popitem()
        ensemble = parent.ensembles.get(ensemble_id, EnsembleModel(ref_url=ensemble_id))
        parent.ensembles[ensemble_id] = ensemble
        return [
            {
                "label": response,
                "value": response,
            }
            for response in ensemble.responses
        ]

    @app.callback(
        Output(parent.uuid("response-selector"), "value"),
        [Input(parent.uuid("response-selector"), "options")],
        [State(parent.uuid("response-selector"), "value")],
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
            {"id": parent.uuid("response-graphic"), "type": parent.uuid("graph")},
            "figure",
        ),
        [
            Input(parent.uuid("response-selector"), "value"),
            Input(parent.uuid("yaxis-type"), "value"),
            Input(parent.uuid("misfits-type"), "value"),
        ],
        [State(parent.uuid("ensemble-selection-store"), "data")],
    )
    def _update_graph(response, yaxis_type, misfits_type, selected_ensembles):
        if response in [None, ""] or not selected_ensembles:
            raise PreventUpdate

        def _generate_plot(ensemble_id, color):
            ensemble = parent.ensembles.get(ensemble_id, None)
            plot = _create_misfits_plot(
                ensemble.responses[response], yaxis_type, None, color
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
        fig.update_yaxes(type=yaxis_type)
        return fig
