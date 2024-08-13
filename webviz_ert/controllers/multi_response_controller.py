import logging
import dash
import pandas as pd
import datetime
import plotly.graph_objects as go
import webviz_ert.assets as assets

from copy import deepcopy
from typing import List, Dict, Union, Any, Optional, Type, Tuple, TYPE_CHECKING
from dash.dependencies import Input, Output, State, ALL, MATCH
from dash.exceptions import PreventUpdate
from webviz_ert.plugins import WebvizErtPluginABC
from webviz_ert.models import (
    ResponsePlotModel,
    Response,
    PlotModel,
    load_ensemble,
    AxisType,
)

if TYPE_CHECKING:
    from .ensemble_model import EnsembleModel

logger = logging.getLogger()


def _get_realizations_plots(
    realizations_df: pd.DataFrame,
    x_axis: Optional[List[Union[int, str, datetime.datetime]]],
    color: str,
    style: Optional[Dict] = None,
    ensemble_name: str = "",
) -> List[PlotModel]:
    if style:
        _style = style
    else:
        _style = assets.ERTSTYLE["response-plot"]["response"].copy()
    _style.update({"line": {"color": color}})
    _style.update({"marker": {"color": color}})
    realizations_data = list()
    for idx, realization in enumerate(realizations_df):
        plot = PlotModel(
            x_axis=x_axis,
            y_axis=realizations_df[realization].values,
            text=f"Realization: {realization} Ensemble: {ensemble_name}",
            name=ensemble_name,
            legendgroup=ensemble_name,
            showlegend=False if idx > 0 else True,
            **_style,
        )
        realizations_data.append(plot)
    return realizations_data


def _get_realizations_statistics_plots(
    df_response: pd.DataFrame,
    x_axis: Optional[List[Union[int, str, datetime.datetime]]],
    color: str,
    ensemble_name: str = "",
) -> List[PlotModel]:
    data = df_response
    p10 = data.quantile(0.1, axis=1)
    p90 = data.quantile(0.9, axis=1)
    _mean = data.mean(axis=1)
    style = deepcopy(assets.ERTSTYLE["response-plot"]["statistics"])
    style["line"]["color"] = color
    style_mean = deepcopy(style)
    style_mean["line"]["dash"] = "solid"
    mean_data = PlotModel(
        x_axis=x_axis,
        y_axis=_mean,
        text=f"Mean",
        name=f"Mean {ensemble_name}",
        **style_mean,
    )
    lower_std_data = PlotModel(
        x_axis=x_axis, y_axis=p10, text="p10 quantile", name="p10 quantile", **style
    )
    upper_std_data = PlotModel(
        x_axis=x_axis, y_axis=p90, text="p90 quantile", name="p90 quantile", **style
    )
    return [mean_data, lower_std_data, upper_std_data]


def _get_observation_plots(
    observation_df: pd.DataFrame,
    metadata: Optional[List[str]] = None,
    ensemble: str = "",
) -> PlotModel:
    data = observation_df["values"]
    stds = observation_df["std"]
    x_axis = observation_df["x_axis"]
    attributes = observation_df["attributes"]
    active_mask = observation_df["active"]

    style = deepcopy(assets.ERTSTYLE["response-plot"]["observation"])
    color = [style["color"] if active else "rgb(0, 0, 0)" for active in active_mask]
    style["marker"]["color"] = color

    observation_data = PlotModel(
        x_axis=x_axis,
        y_axis=data,
        text=attributes,
        name=f"Observation_{ensemble}",
        error_y=dict(
            type="data",  # value of error bar given in data coordinates
            array=stds.values,
            visible=True,
        ),
        meta=metadata,
        **style,
    )
    return observation_data


def _create_response_plot(
    response: Response,
    plot_type: str,
    selected_realizations: List[int],
    color: str,
    style: Optional[Dict] = None,
    ensemble_name: str = "",
) -> ResponsePlotModel:
    x_axis = response.axis
    if plot_type == "Statistics":
        realizations = _get_realizations_statistics_plots(
            response.data_df(selected_realizations),
            x_axis,
            color=color,
            ensemble_name=ensemble_name,
        )
    else:
        realizations = _get_realizations_plots(
            response.data_df(selected_realizations),
            x_axis,
            color=color,
            style=style,
            ensemble_name=ensemble_name,
        )
    if response.observations:
        observations = [
            _get_observation_plots(obs.data_df(), ensemble=ensemble_name)
            for obs in response.observations
        ]
    else:
        observations = []

    ensemble_plot = ResponsePlotModel(realizations, observations, dict())
    return ensemble_plot


def multi_response_controller(parent: WebvizErtPluginABC, app: dash.Dash) -> None:
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
            State(parent.uuid("selected-ensemble-dropdown"), "value"),
            State({"index": MATCH, "type": parent.uuid("response-id-store")}, "data"),
        ],
    )
    def update_graph(
        plot_type: str,
        _: Any,
        selected_ensembles: List[str],
        response: Optional[str],
    ) -> go.Figure:
        if not response or not selected_ensembles:
            raise PreventUpdate

        def _generate_plot(
            ensemble: "EnsembleModel", color: str
        ) -> Optional[ResponsePlotModel]:
            if response not in ensemble.responses:
                return None
            plot = _create_response_plot(
                ensemble.responses[response],
                plot_type,
                [],
                color,
                ensemble_name=ensemble.name,
            )
            return plot

        loaded_ensembles = [
            load_ensemble(parent, ensemble_id) for ensemble_id in selected_ensembles
        ]

        response_plots = [
            _generate_plot(ensemble, assets.get_color(index=index))
            for index, ensemble in enumerate(loaded_ensembles)
        ]

        x_axis_label = axis_label_for_ensemble_response(loaded_ensembles[0], response)

        fig = go.Figure()
        for plot in filter(None, response_plots):
            for realization in plot._realization_plots:
                fig.add_trace(realization.repr)
        for plot in filter(None, response_plots):
            for observation in plot._observations:
                fig.add_trace(observation.repr)
        fig.update_layout(assets.ERTSTYLE["figure"]["layout"])
        fig.update_layout({"xaxis": {"title": {"text": x_axis_label}}})
        fig.update_layout(assets.ERTSTYLE["figure"]["layout-value-y-axis-label"])
        return fig


def axis_label_for_ensemble_response(
    ensemble: "EnsembleModel", response_name: str
) -> str:
    response: Response = ensemble.responses[response_name]
    if response.axis_type == AxisType.TIMESTAMP:
        return "Date"
    return "Index"
