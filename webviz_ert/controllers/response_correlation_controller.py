import pandas as pd
import plotly.graph_objects as go
import dash

from typing import List, Optional, Dict, Tuple, Any, Union
from copy import deepcopy
from dash import dcc, html
from dash.development.base_component import Component
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
from plotly.subplots import make_subplots

from webviz_ert.plugins import WebvizErtPluginABC
from webviz_ert.models import (
    load_ensemble,
    BarChartPlotModel,
    PlotModel,
)
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
            Input(parent.uuid("correlation-store-xindex"), "data"),
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
        corr_xindex: Dict,
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
            for response in responses:
                response_df = ensemble.responses[response].data_df()
                if response_df.empty:
                    continue
                x_index = corr_xindex.get(response, 0)
                parameter_df[response] = response_df.iloc[x_index]
                valid_responses.append(response)

            corrdf = parameter_df.corr(method=correlation_metric)
            corrdf = corrdf.drop(valid_responses, axis=0).fillna(0)
            if selected_response not in valid_responses:
                continue
            if sort_parameters:
                corrdf, df_index = sort_dataframe(corrdf, df_index, selected_response)
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
        Output(
            parent.uuid("response-overview"),
            "figure",
        ),
        [
            Input(parent.uuid("correlation-store-xindex"), "modified_timestamp"),
            Input(parent.uuid("parameter-selection-store-resp"), "modified_timestamp"),
            Input(parent.uuid("ensemble-selection-store"), "modified_timestamp"),
            Input(parent.uuid("correlation-store-selection"), "modified_timestamp"),
        ],
        [
            State(parent.uuid("parameter-selection-store-resp"), "data"),
            State(parent.uuid("ensemble-selection-store"), "data"),
            State(parent.uuid("correlation-store-xindex"), "data"),
            State(parent.uuid("correlation-store-selection"), "data"),
        ],
    )
    def update_response_overview_plot(
        _: Any,
        __: Any,
        ___: Any,
        ____: Any,
        responses: Optional[List[str]],
        ensemble_selection_store: Dict[str, List],
        corr_xindex: Dict,
        corr_param_resp: Dict,
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

                if corr_xindex[selected_response] == 0 and isinstance(
                    response_x_axis, (pd.Index, list)
                ):
                    corr_xindex[selected_response] = _update_corr_index_dict(
                        response_x_axis, response.observations[0].data_df()
                    )

        fig = go.Figure()
        for plot in response_plots:
            fig.add_trace(plot.repr)

        x_axis_label = axis_label_for_ensemble_response(
            loaded_ensembles[0], selected_response
        )

        fig.update_layout(_layout_figure(x_axis_label))

        default_index = 0
        x_index = corr_xindex.get(selected_response, default_index)
        if isinstance(response_x_axis, pd.Index) and not response_x_axis.empty:
            fig.add_shape(
                type="line",
                x0=response_x_axis[x_index],
                y0=0,
                x1=response_x_axis[x_index],
                y1=1,
                yref="paper",
                line=dict(color="rgb(30, 30, 30)", dash="dash", width=3),
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
        ],
    )
    def update_response_parameter_scatterplot(
        corr_xindex: Dict,
        corr_param_resp: Dict,
        parameters: List[str],
        responses: List[str],
        ensembles: List[str],
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

                if isinstance(response.axis, pd.Index) and not response.axis.empty:
                    x_index = corr_xindex.get(selected_response, 0)
                    x_data = response.data_df().iloc[x_index]
                    style = deepcopy(assets.ERTSTYLE["response-plot"]["response-index"])
                    ensemble_color = assets.get_color(index=index)
                    style["marker"]["color"] = ensemble_color
                    _colors[str(ensemble)] = ensemble_color
                    _plots += [
                        PlotModel(
                            x_axis=x_data.values.flatten(),
                            y_axis=y_data.values.flatten(),
                            text="Mean",
                            name=f"{repr(ensemble)}: {selected_response}x{selected_parameter}@{response.axis[x_index]}",
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
            x_axis = ensemble.responses[response_name].axis
            if isinstance(x_axis, pd.Index) and not x_axis.empty:
                x_value = x_axis[corr_xindex.get(response_name, 0)]
                if response_name == selected_response:
                    res_text = f"**{response_name} @ {x_value}**, "
                else:
                    res_text = f"{response_name} @ {x_value}, "
                final_text.append(dcc.Markdown(res_text))
        final_text += [dcc.Markdown(f"parameter: **{corr_param_resp['parameter']}**")]
        return fig, html.Div(final_text)

    @app.callback(
        Output(parent.uuid("correlation-store-xindex"), "data"),
        [
            Input(
                parent.uuid("response-overview"),
                "clickData",
            ),
            Input(parent.uuid("parameter-selection-store-resp"), "data"),
        ],
        [
            State(parent.uuid("correlation-store-xindex"), "data"),
            State(parent.uuid("correlation-store-selection"), "data"),
        ],
    )
    def update_corr_index(
        click_data: Dict, responses: List[str], corr_xindex: Dict, corr_param_resp: Dict
    ) -> Optional[Dict]:
        if not responses:
            raise PreventUpdate

        ctx = dash.callback_context
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if triggered_id == parent.uuid("parameter-selection-store-resp"):
            default_index = 0
            return {
                response: corr_xindex.get(response, default_index)
                for response in responses
            }
        if click_data:
            corr_xindex[corr_param_resp["response"]] = click_data["points"][0][
                "pointIndex"
            ]
        return corr_xindex

    @app.callback(
        Output(parent.uuid("correlation-store-selection"), "data"),
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
        ],
    )
    def update_corr_param_resp(
        click_data: Dict,
        responses: List[str],
        parameters: List[str],
        corr_param_resp: Dict,
    ) -> Optional[Dict]:
        ctx = dash.callback_context
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if triggered_id == parent.uuid("parameter-selection-store-resp") and responses:
            corr_param_resp["response"] = (
                corr_param_resp["response"]
                if corr_param_resp["response"] in responses
                else responses[0]
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
            corr_param_resp["parameter"] = click_data["points"][0]["y"]
            corr_param_resp["response"] = click_data["points"][0]["x"]
        elif not parameters and not responses:
            corr_param_resp["parameter"] = None
            corr_param_resp["response"] = None

        parent.save_state("active_correlation", corr_param_resp)
        return corr_param_resp


def sort_dataframe(
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


def _update_corr_index_dict(
    response_x_axis: Union[pd.Index, list], observation_x_axis: pd.DataFrame
) -> int:
    x_axis_default_observation = _get_first_observation_x(observation_x_axis)
    if isinstance(response_x_axis, pd.Index):
        updated_index = response_x_axis.get_loc(x_axis_default_observation)
    elif isinstance(response_x_axis, list):
        updated_index = response_x_axis.index(x_axis_default_observation)

    return updated_index


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
    caster = {str: int, pd._libs.tslibs.timestamps.Timestamp: str}
    if type(first_observation) not in caster.keys():
        raise ValueError(
            f"invalid obs_data type: should be a str or Timestamp, but it is {type(first_observation)}."
        )

    return caster.get(type(first_observation), lambda *args: False)(first_observation)
