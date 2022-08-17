import pandas as pd
import plotly.graph_objects as go
import dash
import datetime
import numpy as np

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
    Response,
)
from webviz_ert.controllers.multi_response_controller import (
    _get_observation_plots,
    axis_label_for_ensemble_response,
)
from webviz_ert import assets


def response_correlation_controller(parent: WebvizErtPluginABC, app: dash.Dash) -> None:
    DEFAULT_X_INDEX = 0

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
            Input(parent.uuid("correlation-store-xindex"), "data"),
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
        corr_xindex: Dict,
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
            and parameters
            and responses
            and active_resp_param["response"] in responses
        ):
            return ({}, {})

        active_response = active_resp_param["response"]
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
            if active_response not in valid_responses:
                continue
            if sort_parameters:
                corrdf, df_index = _sort_dataframe(corrdf, df_index, active_response)
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
            data[ens_key] = corrdf[active_response]
            data[ens_key].index.name = active_response
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
            Input(
                parent.uuid("correlation-store-active-resp-param"), "modified_timestamp"
            ),
        ],
        [
            State(parent.uuid("parameter-selection-store-resp"), "data"),
            State(parent.uuid("ensemble-selection-store"), "data"),
            State(parent.uuid("correlation-store-xindex"), "data"),
            State(parent.uuid("correlation-store-active-resp-param"), "data"),
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
        active_resp_param: Dict,
    ) -> Optional[go.Figure]:
        ensembles = _get_selected_ensembles_from_store(ensemble_selection_store)
        if not (ensembles and responses and active_resp_param["response"] in responses):
            return {}
        active_response = active_resp_param["response"]
        loaded_ensembles = [
            load_ensemble(parent, ensemble_id) for ensemble_id in ensembles
        ]

        response_plots = []
        obs_plots: List[PlotModel] = []

        for index, ensemble in enumerate(loaded_ensembles):
            response = ensemble.responses[active_response]

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
            loaded_ensembles[0], active_response
        )

        fig.update_layout(_layout_figure(x_axis_label))

        x_index = corr_xindex.get(active_response, DEFAULT_X_INDEX)
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
            Input(parent.uuid("correlation-store-active-resp-param"), "data"),
            Input(parent.uuid("ensemble-selection-store"), "data"),
        ],
        [
            State(parent.uuid("parameter-selection-store-param"), "data"),
            State(parent.uuid("parameter-selection-store-resp"), "data"),
        ],
    )
    def update_response_parameter_scatterplot(
        corr_xindex: Dict,
        active_resp_param: Dict,
        ensemble_selection_store: Dict[str, List],
        parameters: List[str],
        responses: List[str],
    ) -> Optional[Tuple[go.Figure, Component]]:
        ensembles = _get_selected_ensembles_from_store(ensemble_selection_store)
        if not (
            parameters
            and ensembles
            and responses
            and active_resp_param["parameter"] in parameters
            and active_resp_param["response"] in responses
        ):
            return ({}, [])

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
                response = ensemble.responses[active_response]

                if isinstance(response.axis, pd.Index) and not response.axis.empty:
                    x_index = corr_xindex.get(active_response, 0)
                    x_data = response.data_df().iloc[x_index]
                    style = deepcopy(assets.ERTSTYLE["response-plot"]["response-index"])
                    ensemble_color = assets.get_color(index=index)
                    style["marker"]["color"] = ensemble_color
                    _colors[str(ensemble)] = ensemble_color
                    _plots += [
                        PlotModel(
                            x_axis=x_data.values.flatten(),
                            y_axis=y_data.values.flatten(),
                            name=(f"{ensemble.name}"),
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

        specs = _create_scatterplot_specs(
            n_rows, histogram_row_span, spacer_row_span, row_histograms
        )
        fig = make_subplots(
            rows=n_rows,
            cols=2,
            specs=specs,
        )

        formatted_x_value = _format_index_value(response.axis, x_index)
        _set_scatterplot_axes_titles(
            fig, row_histograms, active_response, active_parameter, formatted_x_value
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

        final_text = []
        for response_name in responses:
            x_axis = ensemble.responses[response_name].axis
            if isinstance(x_axis, pd.Index) and not x_axis.empty:
                x_value = x_axis[corr_xindex.get(response_name, 0)]
                if response_name == active_response:
                    res_text = f"**{response_name} @ {x_value}**, "
                else:
                    res_text = f"{response_name} @ {x_value}, "
                final_text.append(dcc.Markdown(res_text))
        final_text += [dcc.Markdown(f"parameter: **{active_resp_param['parameter']}**")]
        return fig, html.Div(final_text)

    @app.callback(
        Output(parent.uuid("correlation-store-xindex"), "data"),
        [
            Input(
                parent.uuid("response-overview"),
                "clickData",
            ),
            Input(parent.uuid("parameter-selection-store-resp"), "data"),
            Input(parent.uuid("ensemble-refresh-button"), "n_clicks"),
        ],
        [
            State(parent.uuid("correlation-store-xindex"), "data"),
            State(parent.uuid("correlation-store-active-resp-param"), "data"),
            State(parent.uuid("ensemble-selection-store"), "data"),
        ],
    )
    def update_corr_index(
        click_data: Dict,
        responses: List[str],
        _: int,
        corr_xindex: Dict,
        active_resp_param: Dict,
        ensemble_selection_store: Dict[str, List],
    ) -> Dict:
        """
        One of the data points we keep track of in the response correlation
        plugin is the current index, representing a point on the x-axis, for
        each selected response.
        Some data shown is a function of the x value represented by that index,
        for example the correlation scatterplot, as well as the heatmap and the
        tornado plot.

        This function updates a dictionary with responses as keys, and the
        current index for each response as values.

        It gets triggered when a user

        - clicks on the response overview plot, effectively choosing an index
        - changes the selection of responses - a default index is assigned

        The default index for a response is
        - zero for responses without observations, representing the smallest
          value for comparable domains, or the first value for categorical
          domains (the domain is represented by the x-axis)
        - the (index of the) smallest or first observation for responses with
          observations

        This dictionary is identical for all ensembles - an assumption in the
        data is that given a response, x-axis and observations for that
        response do not change between ensembles. Yet we need one ensemble to
        determine the default values.
        """
        ctx = dash.callback_context
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if triggered_id == parent.uuid("ensemble-refresh-button"):
            return {}
        if ensemble_selection_store:
            ensembles = [
                selected_ensemble["value"]
                for selected_ensemble in ensemble_selection_store["selected"]
            ]
        else:
            ensembles = None
        if not (responses and ensembles):
            raise PreventUpdate
        ensemble_id = ensembles[0]
        loaded_ensemble = load_ensemble(parent, ensemble_id)

        first_invocation = triggered_id == "" and not click_data

        if triggered_id == parent.uuid("parameter-selection-store-resp") or (
            first_invocation
        ):
            for response_name in responses:
                default_index = _get_default_x_index(
                    loaded_ensemble.responses[response_name]
                )
                corr_xindex[response_name] = corr_xindex.get(
                    response_name, default_index
                )
        elif click_data:
            active_response = active_resp_param["response"]
            corr_xindex[active_response] = click_data["points"][0]["pointIndex"]
        return corr_xindex

    def _get_default_x_index(response: Response) -> int:
        response_x_axis = response.axis
        if response.observations:
            if isinstance(response_x_axis, (pd.Index, list)):
                return _get_first_observation_index(
                    response_x_axis, response.observations[0].data_df()
                )
        return DEFAULT_X_INDEX

    @app.callback(
        Output(parent.uuid("correlation-store-active-resp-param"), "data"),
        [
            Input(
                parent.uuid("response-heatmap"),
                "clickData",
            ),
            Input(parent.uuid("parameter-selection-store-resp"), "data"),
            Input(parent.uuid("parameter-selection-store-param"), "data"),
        ],
        [
            State(parent.uuid("correlation-store-active-resp-param"), "data"),
        ],
    )
    def update_active_resp_param(
        click_data: Dict,
        responses: List[str],
        parameters: List[str],
        active_resp_param: Dict,
    ) -> Dict:
        """
        update_active_resp_param is a callback function responsible for handling
        which response and parameter are active.

        The correlation plots display correlation between a given response and
        paramater (at an index, see `corr_xindex`) for a chosen ensemble. Hence
        the need to keep track of which of potentially many selected responses
        and parameters, respectively, are currently active.

        It should be triggered upon
        - modifying the selection of parameters or responses
        - clicking on the heatmap, effectively choosing a combination of active
          response and parameter

        To avoid saying "response or parameter", we refer to either
        collectively by "variable".

        When the first variable is selected, they become active.
        Further selection of variables does not modify the active variable.
        Deselection of the active variable makes the first selected variable
        active, otherwise deselection does not affect the active state.

        Clicking on the heatmap makes the combination of resoponse and
        parameter active that are represented by the area of the heatmap that
        was clicked.
        """
        ctx = dash.callback_context
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if triggered_id == parent.uuid("parameter-selection-store-resp"):
            if not responses:
                active_resp_param["response"] = None
            elif (
                not active_resp_param["response"]
                or not active_resp_param["response"] in responses
            ):
                active_resp_param["response"] = responses[0]
        elif triggered_id == parent.uuid("parameter-selection-store-param"):
            if not parameters:
                active_resp_param["parameter"] = None
            elif (
                not active_resp_param["parameter"]
                or not active_resp_param["parameter"] in parameters
            ):
                active_resp_param["parameter"] = parameters[0]
        elif click_data:
            active_resp_param["parameter"] = click_data["points"][0]["y"]
            active_resp_param["response"] = click_data["points"][0]["x"]

        parent.save_state("active_correlation", active_resp_param)
        return active_resp_param

    def _get_selected_ensembles_from_store(
        ensemble_selection_store: Dict[str, List]
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


def _get_first_observation_index(
    response_x_axis: Union[pd.Index, list], observation_x_axis: pd.DataFrame
) -> int:
    x_axis_default_observation = _get_first_observation_x(observation_x_axis)
    if isinstance(response_x_axis, pd.Index):
        first_observation_index = response_x_axis.get_loc(x_axis_default_observation)
    elif isinstance(response_x_axis, list):
        first_observation_index = response_x_axis.index(x_axis_default_observation)

    return first_observation_index


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


def _format_index_value(axis: pd.Index, index: int) -> Union[np.number, datetime.date]:
    """_format_index_value takes the value of `axis` at position `index` and
    tries to convert it to a datetime. If this works, it returns just the date.
    If parsing fails, it returns the value unaltered."""
    raw_value = axis[index]
    if isinstance(raw_value, str):
        try:
            datetime_value = pd.to_datetime(raw_value)
            return datetime_value.date()
        except (pd.errors.ParserError, ValueError):
            pass
    return raw_value


def _create_scatterplot_specs(
    n_rows: int, histogram_row_span: int, spacer_row_span: int, row_histograms: int
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
    x_value: Union[datetime.date, np.number],
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
