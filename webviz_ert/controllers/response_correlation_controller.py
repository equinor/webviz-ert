import pandas as pd
import plotly.graph_objects as go
import dash
import numpy as np
import dash_bootstrap_components as dbc

from typing import List, Optional, Dict, Tuple, Any, Union
from copy import deepcopy
from dash import html
from dash.development.base_component import Component
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
from plotly.subplots import make_subplots
from plotly.graph_objs.layout import XAxis, YAxis

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
            Input(parent.uuid("ensemble-selection-store"), "data"),
            Input(parent.uuid("correlation-store-selected-obs"), "data"),
            Input(parent.uuid("correlation-store-active-resp-param"), "data"),
            Input(parent.uuid("correlation-metric"), "value"),
            Input(parent.uuid("sort-parameters"), "on"),
            Input(parent.uuid("hide-hover"), "on"),
        ],
        [
            State(parent.uuid("parameter-selection-store-param"), "data"),
            State(parent.uuid("parameter-selection-store-resp"), "data"),
        ],
    )
    def update_correlation_plot(
        ensemble_selection_store: Dict[str, List],
        selected_obs: Dict,
        active_resp_param: Dict,
        correlation_metric: str,
        sort_parameters: bool,
        hide_hover: bool,
        parameters: List[str],
        responses: List[str],
    ) -> Optional[Tuple[go.Figure, go.Figure]]:
        ensembles = _get_selected_ensembles_from_store(ensemble_selection_store)
        if not (
            ensembles
            and selected_obs
            and parameters
            and responses
            and active_resp_param["response"]["name"] in responses
        ):
            return {}, {}

        active_response = active_resp_param["response"]
        active_response_name = active_response["name"]
        active_index = active_response.get("index")
        if active_index is not None:
            active_response_name = f"{active_response_name}::{active_index}"
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
                resp_indexes = []
                valid_response_with_index = []
                if response.observations:
                    response_axis = response.axis
                    for obs_idx in selected_obs.get(response.name, []):
                        if obs_idx in response_axis:
                            resp_indexes.append(obs_idx)
                            valid_response_with_index.append(
                                f"{response.name}::{obs_idx}"
                            )

                    valid_responses += valid_response_with_index
                    new_dataframe = response.data.loc[resp_indexes].T
                    new_dataframe.columns = valid_response_with_index
                    parameter_df = pd.concat([parameter_df, new_dataframe], axis=1)

            corrdf = parameter_df.corr(method=correlation_metric)
            corrdf = corrdf.drop(valid_responses, axis=0).fillna(0)
            if active_response_name not in valid_responses:
                continue
            if sort_parameters:
                corrdf, df_index = _sort_dataframe(
                    corrdf, df_index, active_response_name
                )
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
            data[ens_key] = corrdf[active_response_name]
            data[ens_key].index.name = active_response_name
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
                heatmap_plot.update_xaxes(
                    showticklabels=True,
                    tickangle=90,
                    ticklabelposition="outside left",
                    row=1,
                    col=1 + idx,
                )
                if hide_hover:
                    heatmap_plot.update_traces(patch={"hoverinfo": "none"})
                else:
                    heatmap_plot.update_traces(
                        patch={"hovertemplate": "%{x} - %{y}: %{z}<extra></extra>"}
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
    def update_observation_index_selector(
        responses: Optional[List[str]],
        ensemble_selection_store: Dict[str, List],
        selected_data: Optional[Dict],
        store_obs_range: Dict,
    ) -> Optional[Tuple[Dict, go.Figure, Dict, Dict]]:
        ctx = dash.callback_context
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

        def disable_figure() -> Tuple[Dict, go.Figure, Dict, Dict]:
            parent.save_state("correlation-store-obs-range", {})
            return {"display": "none", "min-height": "50px"}, go.Figure(), {}, {}

        ensembles = _get_selected_ensembles_from_store(ensemble_selection_store)
        if not (ensembles and responses):
            return disable_figure()
        if triggered_id == parent.uuid("obs_index_selector") and selected_data is None:
            store_obs_range = {}

        if selected_data is None or "range" not in selected_data:
            selected_data = {"range": store_obs_range}

        # Use only one ensemble
        ensemble = load_ensemble(parent, ensembles[0])
        obs_plots: List[PlotModel] = []
        index_axis = False
        time_axis = False
        for idx, response_name in enumerate(responses):
            response = ensemble.responses[response_name]
            if response.observations:
                for obs in response.observations:
                    if not obs.axis:
                        continue
                    if not index_axis and obs.axis_type == AxisType.INDEX:
                        index_axis = True
                    elif not time_axis and obs.axis_type == AxisType.TIMESTAMP:
                        time_axis = True
                    obs_plots.append(_observation_index_plot(obs, response_name, idx))

        if not obs_plots:
            return disable_figure()

        fig = go.Figure(layout_yaxis_range=[-1, len(obs_plots)])
        layout = assets.ERTSTYLE["figure"]["layout"].copy()
        layout.update(
            dict(
                xaxis=XAxis(title="Date", showgrid=False, fixedrange=True),
                xaxis2=XAxis(
                    overlaying="x",
                    title="Index",
                    side="top",
                    showgrid=False,
                    fixedrange=True,
                ),
                yaxis=YAxis(fixedrange=True),
                dragmode="select",
                template="plotly_white",
                height=300,
            )
        )
        fig.update_layout(layout)

        for plot in obs_plots:
            fig.add_trace(plot.repr)

        store_obs_range = selected_data["range"]
        selected_indexes = _get_selected_indexes(obs_plots, store_obs_range)

        # Add selection rectangle to figure
        x_range = store_obs_range.get("x")
        if not time_axis:
            x_range = store_obs_range.get("x2")
        if index_axis and "x2" not in store_obs_range:
            x_range = None

        if selected_indexes and x_range:
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
        else:
            # Use first index if nothing is selected
            for p in obs_plots:
                selected_indexes[p.name] = [p.x_axis[0]]

        parent.save_state("correlation-store-obs-range", store_obs_range)
        return (
            {"min-height": "300px", "padding-top": "20px"},
            fig,
            selected_indexes,
            store_obs_range,
        )

    @app.callback(
        Output(
            parent.uuid("response-overview"),
            "figure",
        ),
        [
            Input(parent.uuid("ensemble-selection-store"), "modified_timestamp"),
            Input(
                parent.uuid("correlation-store-active-resp-param"), "modified_timestamp"
            ),
        ],
        [
            State(parent.uuid("ensemble-selection-store"), "data"),
            State(parent.uuid("correlation-store-active-resp-param"), "data"),
        ],
    )
    def update_response_overview_plot(
        _: Any,
        __: Any,
        ensemble_selection_store: Dict[str, List],
        active_resp_param: Dict,
    ) -> Optional[go.Figure]:
        ensembles = _get_selected_ensembles_from_store(ensemble_selection_store)

        if not (ensembles and active_resp_param["response"]):
            return {}
        active_response = active_resp_param["response"]
        loaded_ensembles = [
            load_ensemble(parent, ensemble_id) for ensemble_id in ensembles
        ]

        response_plots = []
        obs_plots: List[PlotModel] = []

        for index, ensemble in enumerate(loaded_ensembles):
            response = ensemble.responses[active_response["name"]]
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
                    observation_dataframe = obs.data_df()
                    metadata = len(observation_dataframe) * ["observation"]
                    obs_plots.append(
                        _get_observation_plots(observation_dataframe, metadata)
                    )

        fig = go.Figure()
        for plot in response_plots:
            fig.add_trace(plot.repr)

        x_axis_label = axis_label_for_ensemble_response(
            loaded_ensembles[0], active_response["name"]
        )

        fig.update_layout(_layout_figure(x_axis_label))

        selected_obs_idx = active_response.get("index")
        if selected_obs_idx is not None:
            fig.add_vline(
                x=selected_obs_idx,
                line=dict(color="red", dash="dash", width=4),
            )

        for plot in obs_plots:
            fig.add_trace(plot.repr)

        return fig

    @app.callback(
        Output(
            parent.uuid("response-scatterplot"),
            "figure",
        ),
        [
            Input(parent.uuid("correlation-store-active-resp-param"), "data"),
            Input(parent.uuid("ensemble-selection-store"), "data"),
            Input(parent.uuid("correlation-store-selected-obs"), "data"),
        ],
        [
            State(parent.uuid("parameter-selection-store-param"), "data"),
            State(parent.uuid("parameter-selection-store-resp"), "data"),
        ],
    )
    def update_response_parameter_scatterplot(
        active_resp_param: Dict,
        ensemble_selection_store: Dict[str, List],
        _: Dict,
        parameters: List[str],
        responses: List[str],
    ) -> go.Figure:
        ensembles = _get_selected_ensembles_from_store(ensemble_selection_store)
        if not (
            parameters
            and ensembles
            and responses
            and active_resp_param["parameter"] in parameters
            and active_resp_param["response"]
            and active_resp_param["response"]["name"] in responses
        ):
            return {}

        active_parameter = active_resp_param["parameter"]
        active_response = active_resp_param["response"]
        _plots = []
        _resp_plots = {}
        _param_plots = {}
        _colors = {}
        for index, ensemble_id in enumerate(ensembles):
            ensemble = load_ensemble(parent, ensemble_id)
            if ensemble.parameters and ensemble.responses:
                y_data = ensemble.parameters[active_parameter].data_df()
                response = ensemble.responses[active_response["name"]]
                if response.empty:
                    continue
                style = deepcopy(assets.ERTSTYLE["response-plot"]["response-index"])
                ensemble_color = assets.get_color(index=index)
                style["marker"]["color"] = ensemble_color
                _colors[str(ensemble)] = ensemble_color
                active_index: Optional[Any] = active_response.get("index")
                if response.observations:
                    response_axis = response.axis
                    if active_index is not None and active_index in response_axis:
                        x_data = response.data.loc[active_index]
                        _plots += [
                            PlotModel(
                                x_axis=x_data.values.flatten(),
                                y_axis=y_data.values.flatten(),
                                name=f"{ensemble.name}",
                                hoverlabel={"namelength": -1},
                                **style,
                            )
                        ]
                        _resp_plots[str(ensemble)] = x_data.values.flatten()
                        _param_plots[str(ensemble)] = y_data.values.flatten()

        n_rows = 10
        histogram_row_span = 2
        spacer_row_span = 1
        row_histograms = n_rows - (histogram_row_span // 2)

        specs = _create_scatterplot_specs(n_rows, histogram_row_span, spacer_row_span)
        fig = make_subplots(
            rows=n_rows,
            cols=2,
            specs=specs,
        )
        active_index_text = "NA"
        active_index = active_response.get("index")
        if active_index is not None:
            active_index_text = _format_index_text(active_index)
        _set_scatterplot_axes_titles(
            fig, row_histograms, active_response, active_parameter, active_index_text
        )

        _style_scatterplot(fig)

        _add_plots_to_multiplot(
            fig,
            _plots,
            _param_plots,
            _resp_plots,
            _colors,
            row_histograms,
        )

        return fig

    @app.callback(
        Output(parent.uuid("info-text"), "children"),
        [
            Input(parent.uuid("correlation-store-active-resp-param"), "data"),
        ],
    )
    def update_info_text(
        active_resp_param: Dict,
    ) -> List[Component]:
        if not (active_resp_param["response"] and active_resp_param["parameter"]):
            return []
        info_text = []
        active_response = active_resp_param["response"]

        active_index_text = "NA"
        active_index = active_response.get("index")
        if active_index is not None:
            active_index_text = _format_index_text(active_index)
        active_response_text = active_response.get("name")
        active_parameter_text = active_resp_param["parameter"]
        info_text.append(_generate_active_info_piece("RESPONSE", active_response_text))
        info_text.append(_generate_active_info_piece("INDEX", active_index_text))
        info_text.append(
            _generate_active_info_piece("PARAMETER", active_parameter_text)
        )
        return info_text

    @app.callback(
        Output(parent.uuid("correlation-store-active-resp-param"), "data"),
        [
            Input(
                parent.uuid("response-heatmap"),
                "clickData",
            ),
            Input(parent.uuid("parameter-selection-store-resp"), "data"),
            Input(parent.uuid("parameter-selection-store-param"), "data"),
            Input(parent.uuid("correlation-store-selected-obs"), "data"),
        ],
        [
            State(parent.uuid("correlation-store-active-resp-param"), "data"),
        ],
    )
    def update_active_resp_index_and_param(
        click_data: Dict,
        responses: List[str],
        parameters: List[str],
        selected_obs: Dict,
        active_resp_param: Dict,
    ) -> Dict:
        """
        update_active_resp_param is a callback function responsible for handling
        which response index and parameter are active.

        The correlation plots display correlation between a given response(at an index)
        and parameter for a chosen ensemble.

        It should be triggered upon
        - modifying the selection of parameters or responses
        - clicking on the heatmap, effectively choosing a combination of active
          response at an index and parameter
        - selection a new range in the response observation selector

        To avoid saying "response or parameter", we refer to either
        collectively by "variable".

        When the first variable is selected, they become active.
        Further selection of variables does not modify the active variable.
        Deselection of the active variable makes the first selected variable
        active, otherwise deselection does not affect the active state.

        Clicking on the heatmap makes the combination of response index and
        parameter active that are represented by the area of the heatmap that
        was clicked.
        """
        ctx = dash.callback_context
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if not triggered_id:
            raise PreventUpdate
        if triggered_id == parent.uuid("parameter-selection-store-resp"):
            if not responses:
                active_resp_param["response"] = None
            elif selected_obs and (
                not active_resp_param["response"]
                or not active_resp_param["response"]["name"] in responses
            ):
                response_name = next(iter(selected_obs.keys()))
                active_resp_param["response"] = {
                    "name": response_name,
                    "index": selected_obs[response_name][0],
                }
            elif selected_obs:
                response_name = active_resp_param["response"]["name"]
                response_index = active_resp_param["response"]["index"]
                if response_index not in selected_obs[response_name]:
                    active_resp_param["response"]["index"] = selected_obs[
                        response_name
                    ][0]

        elif triggered_id == parent.uuid("parameter-selection-store-param"):
            if not parameters:
                active_resp_param["parameter"] = None
            elif (
                not active_resp_param["parameter"]
                or not active_resp_param["parameter"] in parameters
            ):
                active_resp_param["parameter"] = parameters[0]
        elif triggered_id == parent.uuid("correlation-store-selected-obs"):
            if active_resp_param["response"] and selected_obs:
                response_name = active_resp_param["response"]["name"]
                if response_name in selected_obs:
                    active_resp_param["response"]["index"] = selected_obs[
                        response_name
                    ][0]
                else:
                    response_name = next(iter(selected_obs.keys()))
                    active_resp_param["response"] = {
                        "name": response_name,
                        "index": selected_obs[response_name][0],
                    }
        elif click_data:
            if "::" in click_data["points"][0]["x"]:
                resp_name, index = click_data["points"][0]["x"].split("::", maxsplit=1)
                index = _format_index_value(index)
            else:
                resp_name = click_data["points"][0]["x"]
                index = 0

            active_resp_param["parameter"] = click_data["points"][0]["y"]
            active_resp_param["response"] = {"name": resp_name, "index": index}
        elif not parameters and not responses:
            active_resp_param["parameter"] = None
            active_resp_param["response"] = None

        parent.save_state("active_correlation", active_resp_param)
        return active_resp_param


def _get_selected_ensembles_from_store(
    ensemble_selection_store: Dict[str, List],
) -> Optional[List[str]]:
    if ensemble_selection_store:
        return [
            selection["value"] for selection in ensemble_selection_store["selected"]
        ]
    return None


def _sort_dataframe(
    dataframe: pd.core.frame.DataFrame,
    index: Optional[pd.core.indexes.base.Index],
    sort_by_column: str,
) -> Tuple[pd.core.frame.DataFrame, pd.core.indexes.base.Index]:
    if index is None:
        index = dataframe[sort_by_column].abs().sort_values().index.copy()
    dataframe = dataframe.reindex(index)
    return dataframe, index


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


def _format_index_value(raw_index: Union[str, int]) -> Union[str, int]:
    try:
        return int(raw_index)
    except (TypeError, ValueError):
        return raw_index


def _format_index_text(raw_index: Union[str, int]) -> str:
    formatted_index = _format_index_value(raw_index)
    if isinstance(formatted_index, int):
        return str(formatted_index)
    else:
        try:
            return str(pd.Timestamp(raw_index).date())
        except (TypeError, ValueError):
            return str(raw_index)


def _create_scatterplot_specs(
    n_rows: int,
    histogram_row_span: int,
    spacer_row_span: int,
) -> List[List[Optional[Dict[str, int]]]]:
    specs: List[List[Optional[Dict[str, int]]]] = [
        [
            {
                "colspan": 2,
                "rowspan": n_rows - spacer_row_span - histogram_row_span,
            },
            None,
        ]
    ]
    # insert blanks into rows between scatterplot and histograms
    # sadly mypy cannot deal with this short hand notation
    specs += (n_rows - 1 - histogram_row_span) * [[None, None]]  # type:ignore
    specs.append([{"rowspan": histogram_row_span}, {"rowspan": histogram_row_span}])
    # insert blanks under histograms
    specs += (histogram_row_span - 1) * [[None, None]]  # type:ignore
    return specs


def _set_scatterplot_axes_titles(
    fig: go.Figure,
    row_histograms: int,
    active_response: str,
    active_parameter: str,
    x_value: Union[str, np.number],
) -> None:
    fig.update_xaxes(title_text=f"{active_response} @ {x_value}", row=1, col=1)
    fig.update_yaxes(title_text=f"{active_parameter}", row=1, col=1)
    fig.update_xaxes(title_text=f"{active_parameter}", row=row_histograms, col=1)
    fig.update_xaxes(title_text=f"{active_response}", row=row_histograms, col=2)


def _style_scatterplot(
    fig: go.Figure,
) -> None:
    fig.update_layout(assets.ERTSTYLE["figure"]["layout"])
    fig.update_layout(showlegend=False)


def _add_plots_to_multiplot(
    fig: go.Figure,
    _plots: List[PlotModel],
    _param_plots: Dict[str, np.ndarray],
    _resp_plots: Dict[str, np.ndarray],
    _colors: Dict[str, str],
    row_histograms: int,
) -> None:
    for plot in _plots:
        fig.add_trace(plot.repr, 1, 1)

    for ensemble_name in _param_plots:
        fig.add_trace(
            {
                "type": "histogram",
                "name": f"{ensemble_name}",
                "hoverlabel": {
                    "namelength": -1,
                },
                "x": _param_plots[ensemble_name],
                "showlegend": False,
                "marker_color": _colors[ensemble_name],
            },
            row_histograms,
            1,
        )
    for ensemble_name in _resp_plots:
        fig.add_trace(
            {
                "type": "histogram",
                "name": f"{ensemble_name}",
                "hoverlabel": {
                    "namelength": -1,
                },
                "x": _resp_plots[ensemble_name],
                "showlegend": False,
                "marker_color": _colors[ensemble_name],
            },
            row_histograms,
            2,
        )


def _generate_active_info_piece(title: str, value: str) -> Component:
    return html.Span(
        [
            f"{title}: ",
            dbc.Badge(
                value,
            ),
        ]
    )


def _get_selected_indexes(plots: List[PlotModel], data_range: Optional[Dict]) -> Dict:
    selected_indexes: Dict = {}
    if not data_range:
        return selected_indexes
    time_range = data_range.get("x")
    index_range = data_range.get("x2")
    for plot in plots:
        if plot.axis_type == AxisType.INDEX and index_range:
            indexes_in_range = plot.indexes_in_range(index_range)
        elif plot.axis_type == AxisType.TIMESTAMP and time_range:
            indexes_in_range = plot.indexes_in_range(time_range)
        else:
            continue
        if indexes_in_range:
            selected_indexes[plot.name] = indexes_in_range

    return selected_indexes


def _observation_index_plot(obs: Any, name: str, plot_idx: int) -> PlotModel:
    style = deepcopy(assets.ERTSTYLE["observation-selection-plot"])
    marker_color = assets.get_color(plot_idx)
    style.update(
        dict(
            marker={"color": marker_color, "size": 9},
            xaxis="x2" if obs.axis_type == AxisType.INDEX else "x",
        )
    )
    return PlotModel(
        x_axis=obs.axis,
        y_axis=[str(plot_idx) for _ in range(len(obs.axis))],
        text=obs.name,
        name=name,
        **style,
    )
