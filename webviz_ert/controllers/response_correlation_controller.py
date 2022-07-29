import numpy
import pandas as pd
from pandas._libs.tslibs.timestamps import Timestamp
import plotly.graph_objects as go
import dash
import dateutil.parser

from typing import List, Optional, Dict, Tuple, Any, Union
from copy import deepcopy
from dash import dcc, html
from dash.development.base_component import Component
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
from plotly.subplots import make_subplots
from plotly.graph_objs.layout import XAxis

from webviz_ert.plugins import WebvizErtPluginABC
from webviz_ert.models import load_ensemble, BarChartPlotModel, PlotModel, AxisType
from webviz_ert.controllers.multi_response_controller import (
    _get_observation_plots,
    axis_label_for_ensemble_response,
)
from webviz_ert import assets


def response_correlation_controller(parent: WebvizErtPluginABC, app: dash.Dash) -> None:
    @app.callback(
        [
            Output(
                parent.uuid("response-correlation"),
                "figure",
            ),
            Output(
                parent.uuid("response-heatmap"),
                "figure",
            ),
        ],
        [
            Input(parent.uuid("correlation-store-selected-obs"), "data"),
            Input(parent.uuid("correlation-store-selection"), "data"),
            Input(parent.uuid("correlation-metric"), "value"),
            Input(parent.uuid("sort-parameters"), "on"),
            Input(parent.uuid("hide-hover"), "on"),
        ],
        [
            State(parent.uuid("parameter-selection-store-param"), "data"),
            State(parent.uuid("parameter-selection-store-resp"), "data"),
            State(parent.uuid("selected-ensemble-dropdown"), "value"),
        ],
    )
    def update_correlation_plot(
        selected_obs: Dict,
        corr_param_resp: Dict,
        correlation_metric: str,
        sort_parameters: bool,
        hide_hover: bool,
        parameters: List[str],
        responses: List[str],
        ensembles: List[str],
    ) -> Optional[Tuple[go.Figure, go.Figure]]:
        if not (
            ensembles
            and parameters
            and responses
            and corr_param_resp["response"] in responses
        ):
            raise PreventUpdate
        selected_response = corr_param_resp["response"]
        data = {}
        colors = {}
        heatmaps = []

        df_index = None
        for index, ensemble_id in enumerate(ensembles):
            ensemble = load_ensemble(parent, ensemble_id)
            parameter_df = ensemble.parameters_df(parameters)
            if parameter_df.empty:
                continue
            valid_responses = []
            for response_name in responses:
                response = ensemble.responses[response_name]
                if response.empty:
                    continue
                if response.observations:
                    for obs in response.observations:
                        for idx, obs_idx in enumerate(selected_obs.get(obs.name, [])):
                            if obs.axis_type == AxisType.TIMESTAMP:
                                resp_index = str(Timestamp(obs_idx))
                            else:
                                resp_index = obs_idx
                            parameter_df[f"{response.name}::{idx}"] = response.data.loc[
                                resp_index
                            ]
                            valid_responses.append(f"{response.name}::{idx}")
                else:
                    # TODO: consider removing this else clause not really
                    #  any point is showing responses without observations but here for now
                    parameter_df[response_name] = response.data.iloc[0]
                    valid_responses.append(response_name)
            corrdf = parameter_df.corr(method=correlation_metric)
            corrdf = corrdf.drop(valid_responses, axis=0).fillna(0)
            selected_response = f"{selected_response}::0"
            if selected_response not in valid_responses:
                continue
            if sort_parameters:
                corrdf, df_index = _sort_dataframe(corrdf, df_index, selected_response)
            # create heatmap
            data_heatmap = {
                "type": "heatmap",
                "x": corrdf[valid_responses].columns,
                "y": corrdf[valid_responses].index,
                "z": [
                    corrdf[valid_responses].loc[parameter].values
                    for parameter in corrdf.index
                ],
                "zmin": -1,
                "zmax": 1,
                "colorscale": "rdylbu",
                "reversescale": True,
            }
            heatmaps.append(data_heatmap)
            ens_key = repr(ensemble)
            data[ens_key] = corrdf[selected_response]
            data[ens_key].index.name = selected_response
            colors[ens_key] = assets.get_color(index=index)
        if data and heatmaps:
            correlation_plot = BarChartPlotModel(data, colors)
            heatmap_plot = make_subplots(
                rows=1,
                cols=len(heatmaps),
                subplot_titles=[f"ENS_{idx + 1}" for idx, _ in enumerate(heatmaps)],
            )

            for idx, heatmap in enumerate(heatmaps):
                heatmap_plot.add_trace(heatmap, 1, 1 + idx)
                heatmap_plot.update_yaxes(showticklabels=False, row=1, col=1 + idx)
                heatmap_plot.update_xaxes(showticklabels=False, row=1, col=1 + idx)
                if hide_hover:
                    heatmap_plot.update_traces(patch={"hoverinfo": "none"})
                else:
                    heatmap_plot.update_traces(
                        patch={"hovertemplate": "%{y}: %{z}<extra></extra>"}
                    )
            _layout = assets.ERTSTYLE["figure"]["layout"].copy()

            _layout.update(
                {
                    "clickmode": "event+select",
                    "showlegend": False,
                    "annotations": [{"font": {"color": colors[ens]}} for ens in colors],
                    "hoverlabel": {
                        "font": {
                            "size": 10,
                        },
                    },
                }
            )
            heatmap_plot.update_layout(_layout)

            y_pos = len(corrdf[valid_responses].index)
            for i, _ in enumerate(heatmaps):
                for j, label in enumerate(corrdf[valid_responses].columns):
                    heatmap_plot.add_annotation(
                        x=j,
                        y=y_pos - 0.55,
                        text=label,
                        textangle=90,
                        showarrow=False,
                        col=1 + i,
                        row=1,
                        yref="paper",
                        yanchor="top",
                    )

            return correlation_plot.repr, heatmap_plot
        raise PreventUpdate

    @app.callback(
        [
            Output(parent.uuid("obs_index_selector_container"), "style"),
            Output(parent.uuid("obs_index_selector"), "figure"),
            Output(parent.uuid("correlation-store-selected-obs"), "data"),
            Output(parent.uuid("correlation-store-obs-range"), "data"),
        ],
        [
            Input(parent.uuid("parameter-selection-store-resp"), "data"),
            Input(parent.uuid("ensemble-selection-store"), "data"),
            Input(parent.uuid("obs_index_selector"), "selectedData"),
        ],
        [
            State(parent.uuid("correlation-store-obs-range"), "data"),
        ],
    )
    def update_obs_selector_plot(
        responses: Optional[List[str]],
        ensemble_selection_store: Dict[str, List],
        selected_data: Optional[Dict],
        store_obs_range: Dict,
    ) -> Optional[Tuple[Dict, go.Figure, Dict, Dict]]:
        if responses is None:
            responses = []
        ctx = dash.callback_context
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if not ensemble_selection_store and not triggered_id:
            raise PreventUpdate

        if triggered_id == parent.uuid("obs_index_selector") and not selected_data:
            store_obs_range = {}
        if store_obs_range and not selected_data:
            selected_data = {"range": store_obs_range}
        ensembles = []
        if ensemble_selection_store:
            ensembles = [
                selected_ensemble["value"]
                for selected_ensemble in ensemble_selection_store["selected"]
            ]
        obs_plots: List[PlotModel] = []
        loaded_ensembles = [
            load_ensemble(parent, ensemble_id) for ensemble_id in ensembles
        ]

        index_axis = False
        time_axis = False
        for ens_idx, ensemble in enumerate(loaded_ensembles):
            for idx, response_name in enumerate(responses):
                response = ensemble.responses[response_name]
                if response.observations:
                    for obs in response.observations:
                        x_axis = obs.axis
                        if (
                            x_axis is None
                            or isinstance(x_axis, pd.Index)
                            and x_axis.empty
                        ):
                            continue
                        style = deepcopy(assets.ERTSTYLE["observation-selection-plot"])
                        if obs.axis_type == AxisType.INDEX:
                            index_axis = True
                            style.update({"xaxis": "x2"})
                        else:
                            time_axis = True
                        obs_color = assets.get_color(index=idx)
                        style["marker"].update({"color": obs_color})
                        obs_plots.append(
                            PlotModel(
                                x_axis=x_axis,
                                y_axis=[str(idx) for _ in range(len(x_axis))],
                                text=obs.name,
                                name=obs.name,
                                **style,
                            )
                        )

        if not obs_plots:
            store_obs_range = {}
            selected_indexes: Dict = {}
            parent.save_state("correlation-store-obs-range", store_obs_range)
            return (
                {"display": "none", "min-height": "50px"},
                go.Figure(),
                selected_indexes,
                store_obs_range,
            )

        fig = go.Figure(layout_yaxis_range=[-1, len(obs_plots)])
        layout = assets.ERTSTYLE["figure"]["layout"].copy()
        layout.update(
            dict(
                xaxis=XAxis(title="Date", showgrid=False),
                dragmode="select",
                template="plotly_white",
            )
        )

        if index_axis:
            layout.update(
                dict(
                    xaxis2=XAxis(
                        overlaying="x",
                        title="Index",
                        side="top",
                        showgrid=False,
                    )
                )
            )
        fig.update_layout(layout)

        selected_indexes = _get_selected_indexes(obs_plots, selected_data)
        for plot in obs_plots:
            fig.add_trace(plot.repr)

        if selected_data:
            # Add selection rectangle to figure
            store_obs_range = selected_data["range"]
            x_range = None
            if time_axis:
                x_range = store_obs_range.get("x")
            elif index_axis:
                x_range = store_obs_range.get("x2")
            if time_axis and index_axis:
                if "x" not in store_obs_range or "x2" not in store_obs_range:
                    x_range = None

            if x_range:
                x_start, x_end = x_range
                fig.add_shape(
                    type="rect",
                    yref="paper",
                    x0=x_start,
                    y0=0,
                    x1=x_end,
                    y1=1,
                    fillcolor="PaleTurquoise",
                    opacity=0.35,
                )
        parent.save_state("correlation-store-obs-range", store_obs_range)
        return {"min-height": "500px"}, fig, selected_indexes, store_obs_range

    @app.callback(
        Output(
            parent.uuid("response-overview"),
            "figure",
        ),
        [
            Input(parent.uuid("correlation-store-xindex"), "modified_timestamp"),
            Input(parent.uuid("parameter-selection-store-resp"), "modified_timestamp"),
            Input(parent.uuid("ensemble-selection-store"), "modified_timestamp"),
            Input(parent.uuid("correlation-store-selection"), "modified_timestamp"),
            Input(parent.uuid("correlation-store-selected-obs"), "modified_timestamp"),
        ],
        [
            State(parent.uuid("parameter-selection-store-resp"), "data"),
            State(parent.uuid("ensemble-selection-store"), "data"),
            State(parent.uuid("correlation-store-xindex"), "data"),
            State(parent.uuid("correlation-store-selection"), "data"),
            State(parent.uuid("correlation-store-selected-obs"), "data"),
        ],
    )
    def update_response_overview_plot(
        _: Any,
        __: Any,
        ___: Any,
        ____: Any,
        _____: Any,
        responses: Optional[List[str]],
        ensemble_selection_store: Dict[str, List],
        corr_xindex: Dict,
        corr_param_resp: Dict,
        selected_obs: Dict,
    ) -> Optional[go.Figure]:
        if ensemble_selection_store:
            ensembles = [
                selected_ensemble["value"]
                for selected_ensemble in ensemble_selection_store["selected"]
            ]
        else:
            ensembles = None
        if not (ensembles and responses and corr_param_resp["response"] in responses):
            raise PreventUpdate
        selected_response = corr_param_resp["response"]
        loaded_ensembles = [
            load_ensemble(parent, ensemble_id) for ensemble_id in ensembles
        ]

        response_plots = []
        obs_plots: List[PlotModel] = []

        for index, ensemble in enumerate(loaded_ensembles):
            response = ensemble.responses[selected_response]

            response_x_axis = response.axis

            if isinstance(response_x_axis, pd.Index) and response_x_axis.empty:
                continue

            if response_x_axis is not None:
                style = _define_style_ensemble(index, response_x_axis)

            response_df = response.data_df().copy()
            response_plots += [
                PlotModel(
                    x_axis=response_x_axis,
                    y_axis=response_df[realization],
                    text=realization,
                    name=realization,
                    **style,
                )
                for realization in response_df
            ]

            if response.observations:
                for obs in response.observations:
                    obs_plots.append(_get_observation_plots(obs.data_df()))

        fig = go.Figure()
        for plot in response_plots:
            fig.add_trace(plot.repr)

        x_axis_label = axis_label_for_ensemble_response(
            loaded_ensembles[0], selected_response
        )

        fig.update_layout(_layout_figure(x_axis_label))

        for ensemble in loaded_ensembles:
            response = ensemble.responses[selected_response]
            if response.empty:
                continue
            if response.observations:
                selected_obs_idx = corr_xindex.get(selected_response)
                for obs in response.observations:
                    for obs_idx, x_idx in enumerate(selected_obs.get(obs.name, [])):
                        line_color = "rgb(30, 30, 30)"
                        if obs_idx == selected_obs_idx:
                            line_color = "red"
                        fig.add_vline(
                            x=x_idx,
                            line=dict(color=line_color, dash="dash", width=2),
                        )

        for plot in obs_plots:
            fig.add_trace(plot.repr)

        return fig

    @app.callback(
        [
            Output(
                parent.uuid("response-scatterplot"),
                "figure",
            ),
            Output(parent.uuid("response-info-text"), "children"),
        ],
        [
            Input(parent.uuid("correlation-store-xindex"), "data"),
            Input(parent.uuid("correlation-store-selection"), "data"),
        ],
        [
            State(parent.uuid("parameter-selection-store-param"), "data"),
            State(parent.uuid("parameter-selection-store-resp"), "data"),
            State(parent.uuid("selected-ensemble-dropdown"), "value"),
            State(parent.uuid("correlation-store-selected-obs"), "data"),
        ],
    )
    def update_response_parameter_scatterplot(
        corr_xindex: Dict,
        corr_param_resp: Dict,
        parameters: List[str],
        responses: List[str],
        ensembles: List[str],
        selected_obs: Dict,
    ) -> Optional[Tuple[go.Figure, Component]]:

        if not (
            parameters
            and ensembles
            and responses
            and corr_param_resp["parameter"] in parameters
            and corr_param_resp["response"] in responses
        ):
            raise PreventUpdate

        selected_parameter = corr_param_resp["parameter"]
        selected_response = corr_param_resp["response"]
        _plots = []
        _resp_plots = {}
        _param_plots = {}
        _colors = {}
        for index, ensemble_id in enumerate(ensembles):
            ensemble = load_ensemble(parent, ensemble_id)

            if ensemble.parameters and ensemble.responses:
                y_data = ensemble.parameters[selected_parameter].data_df()
                response = ensemble.responses[selected_response]
                if response.empty:
                    continue
                style = deepcopy(assets.ERTSTYLE["response-plot"]["response-index"])
                ensemble_color = assets.get_color(index=index)
                style["marker"]["color"] = ensemble_color
                _colors[str(ensemble)] = ensemble_color
                obs_idx = corr_xindex.get(selected_response, 0)
                if response.observations:
                    for obs in response.observations:
                        selected_obs_indexes = selected_obs.get(obs.name, None)
                        if selected_obs_indexes is None:
                            continue
                        if obs.axis_type == AxisType.TIMESTAMP:
                            resp_index = str(Timestamp(selected_obs_indexes[obs_idx]))
                        else:
                            resp_index = selected_obs_indexes[obs_idx]

                        x_data = response.data.loc[resp_index]
                        _plots += [
                            PlotModel(
                                x_axis=x_data.values.flatten(),
                                y_axis=y_data.values.flatten(),
                                text="Mean",
                                name=f"{repr(ensemble)}: {selected_response}x{selected_parameter}@{obs_idx}",
                                **style,
                            )
                        ]
                        _resp_plots[str(ensemble)] = x_data.values.flatten()
                        _param_plots[str(ensemble)] = y_data.values.flatten()
                else:
                    x_data = response.data.iloc[0]
                    resp_x_index = None
                    if response.axis is not None:
                        resp_x_index = response.axis[0]
                    _plots += [
                        PlotModel(
                            x_axis=x_data.values.flatten(),
                            y_axis=y_data.values.flatten(),
                            text="Mean",
                            name=f"{repr(ensemble)}: {selected_response}x{selected_parameter}@{resp_x_index}",
                            **style,
                        )
                    ]
                    _resp_plots[str(ensemble)] = x_data.values.flatten()
                    _param_plots[str(ensemble)] = y_data.values.flatten()

        fig = make_subplots(
            rows=4,
            cols=2,
            specs=[
                [{"colspan": 2, "rowspan": 3}, None],
                [None, None],
                [None, None],
                [{"rowspan": 1}, {"rowspan": 1}],
            ],
        )
        for plot in _plots:
            fig.add_trace(plot.repr, 1, 1)

        for key in _param_plots:
            fig.add_trace(
                {
                    "type": "histogram",
                    "x": _param_plots[key],
                    "showlegend": False,
                    "marker_color": _colors[key],
                },
                4,
                1,
            )
        for key in _resp_plots:
            fig.add_trace(
                {
                    "type": "histogram",
                    "x": _resp_plots[key],
                    "showlegend": False,
                    "marker_color": _colors[key],
                },
                4,
                2,
            )
        fig.update_layout(assets.ERTSTYLE["figure"]["layout"])
        fig.update_layout(showlegend=False)
        final_text = []
        for response_name in responses:
            response = ensemble.responses[response_name]
            if not response.empty:
                obs_idx = corr_xindex.get(response_name, 0)
                if response_name == selected_response:
                    res_text = f"**{response_name} @ {obs_idx}**, "
                else:
                    res_text = f"{response_name} @ {obs_idx}, "
                final_text.append(dcc.Markdown(res_text))
        final_text += [dcc.Markdown(f"parameter: **{corr_param_resp['parameter']}**")]
        return fig, html.Div(final_text)

    @app.callback(
        [
            Output(parent.uuid("correlation-store-selection"), "data"),
            Output(parent.uuid("correlation-store-xindex"), "data"),
        ],
        [
            Input(
                parent.uuid("response-heatmap"),
                "clickData",
            ),
            Input(parent.uuid("parameter-selection-store-resp"), "data"),
            Input(parent.uuid("parameter-selection-store-param"), "data"),
        ],
        [
            State(parent.uuid("correlation-store-selection"), "data"),
            State(parent.uuid("correlation-store-xindex"), "data"),
        ],
    )
    def update_corr_param_resp(
        click_data: Dict,
        responses: List[str],
        parameters: List[str],
        corr_param_resp: Dict,
        corr_xindex: Dict,
    ) -> Optional[Tuple[Dict, Dict]]:
        ctx = dash.callback_context
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if triggered_id == parent.uuid("parameter-selection-store-resp") and responses:
            corr_param_resp["response"] = (
                corr_param_resp["response"]
                if corr_param_resp["response"] in responses
                else responses[0]
            )
            corr_xindex.update(
                {response: 0 for response in responses if response not in corr_xindex}
            )
        elif (
            triggered_id == parent.uuid("parameter-selection-store-param")
            and parameters
        ):
            corr_param_resp["parameter"] = (
                corr_param_resp["parameter"]
                if corr_param_resp["parameter"] in parameters
                else parameters[0]
            )
        elif click_data:
            if "::" in click_data["points"][0]["x"]:
                resp_name, index = click_data["points"][0]["x"].split("::", maxsplit=1)
                index = int(index)
            else:
                resp_name = click_data["points"][0]["x"]
                index = 0

            corr_param_resp["parameter"] = click_data["points"][0]["y"]
            corr_param_resp["response"] = resp_name
            corr_xindex.update({resp_name: index})
        elif not parameters and not responses:
            corr_param_resp["parameter"] = None
            corr_param_resp["response"] = None

        parent.save_state("active_correlation", corr_param_resp)
        return corr_param_resp, corr_xindex


def _sort_dataframe(
    dataframe: pd.core.frame.DataFrame,
    index: Optional[pd.core.indexes.base.Index],
    sort_by_column: str,
) -> Tuple[pd.core.frame.DataFrame, pd.core.indexes.base.Index]:
    if index is None:
        index = dataframe[sort_by_column].abs().sort_values().index.copy()
    dataframe = dataframe.reindex(index)
    return dataframe, index


def _get_selected_indexes(
    plots: List[PlotModel], selected_data: Optional[Dict]
) -> Dict:
    selected_indexes: Dict = {}
    if not selected_data:
        return selected_indexes
    for plot in plots:
        selected_indexes[plot.name] = []
        x_data_range = selected_data["range"].get("x")
        x2_data_range = selected_data["range"].get("x2")
        if plot.axis_type == AxisType.INDEX:
            if not x2_data_range:
                continue
            x_start, x_end = x2_data_range
        elif not x_data_range:
            continue
        else:
            x_start = dateutil.parser.isoparse(x_data_range[0])
            x_end = dateutil.parser.isoparse(x_data_range[1])

        for val in plot._x_axis:
            if x_start <= val <= x_end:
                selected_indexes[plot.name].append(val)
    return selected_indexes


def _define_style_ensemble(index: int, x_axis: pd.Index) -> Dict:
    if str(x_axis[0]).isnumeric():
        style = deepcopy(assets.ERTSTYLE["response-plot"]["response-index"])
    else:
        style = deepcopy(assets.ERTSTYLE["response-plot"]["response"])
    ensemble_color = assets.get_color(index=index)
    style.update({"marker": {"color": ensemble_color}})
    style.update({"line": {"color": ensemble_color}})

    return style


def _layout_figure(x_axis_label: str) -> dict:
    layout = assets.ERTSTYLE["figure"]["layout"].copy()
    layout.update(dict(showlegend=False))
    layout.update(clickmode="event+select")
    layout.update({"xaxis": {"title": {"text": x_axis_label}}})
    layout.update(assets.ERTSTYLE["figure"]["layout-value-y-axis-label"])

    return layout


def _get_first_observation_x(obs_data: pd.DataFrame) -> Union[int, str]:
    """
    :return: The first x value in the observation data, converted
        to type suitable for lookup in the response vector.
    """
    first_observation = obs_data["x_axis"][0]
    caster = {str: int, Timestamp: str, numpy.int64: int}
    if type(first_observation) not in caster.keys():
        raise ValueError(
            f"Invalid obs_data type: should be an Int or Timestamp, but it is {type(first_observation)}."
        )

    return caster.get(type(first_observation), lambda *args: False)(first_observation)
