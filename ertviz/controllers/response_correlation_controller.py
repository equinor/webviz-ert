import plotly.graph_objects as go
from plotly.subplots import make_subplots
from copy import deepcopy
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash
from ertviz.models import (
    load_ensemble,
    BarChartPlotModel,
    PlotModel,
)
from ertviz.controllers.multi_response_controller import (
    _get_observation_plots,
)
import ertviz.assets as assets


def response_correlation_controller(parent, app):
    @app.callback(
        [
            Output(
                {
                    "id": parent.uuid("response-correlation"),
                    "type": parent.uuid("graph"),
                },
                "figure",
            ),
            Output(
                {
                    "id": parent.uuid("response-heatmap"),
                    "type": parent.uuid("graph"),
                },
                "figure",
            ),
        ],
        [
            Input(parent.uuid("correlation-store-xindex"), "data"),
            Input(parent.uuid("correlation-store-selection"), "data"),
            Input(parent.uuid("correlation-metric"), "value"),
        ],
        [
            State(parent.uuid("parameter-selection-store-param"), "data"),
            State(parent.uuid("parameter-selection-store-resp"), "data"),
            State(parent.uuid("ensemble-selection-store"), "data"),
        ],
    )
    def update_correlation_plot(
        corr_xindex,
        corr_param_resp,
        correlation_metric,
        parameters,
        responses,
        ensembles,
    ):
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
        for ensemble_id, color in ensembles.items():
            ensemble = load_ensemble(parent, ensemble_id)
            parameter_df = ensemble.parameters_df(parameters)
            for response in responses:
                response_df = ensemble.responses[response].data_df()
                x_index = corr_xindex.get(response, 0)
                parameter_df[response] = response_df.iloc[x_index]

            corrdf = parameter_df.corr(method=correlation_metric)
            corrdf = corrdf.drop(responses, axis=0).fillna(0)
            if df_index is None:
                df_index = corrdf[selected_response].abs().sort_values().index.copy()
            corrdf = corrdf.reindex(df_index)
            # create heatmap
            data_heatmap = {
                "type": "heatmap",
                "x": corrdf[responses].columns,
                "y": corrdf[responses].index,
                "z": [
                    corrdf[responses].loc[parameter].values
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
            colors[ens_key] = color["color"]
        if data and heatmaps:
            parent.correlation_plot = BarChartPlotModel(data, colors)
            parent.heatmap_plot = make_subplots(
                rows=1,
                cols=len(heatmaps),
                subplot_titles=[f"ENS_{idx + 1}" for idx, _ in enumerate(heatmaps)],
            )
            for idx, heatmap in enumerate(heatmaps):
                parent.heatmap_plot.add_trace(heatmap, 1, 1 + idx)
                parent.heatmap_plot.update_yaxes(
                    showticklabels=False, row=1, col=1 + idx
                )
                parent.heatmap_plot.update_xaxes(
                    showticklabels=False, row=1, col=1 + idx
                )
            _layout = assets.ERTSTYLE["figure"]["layout"].copy()
            _layout.update(
                {
                    "clickmode": "event+select",
                    "showlegend": False,
                    "annotations": [{"font": {"color": colors[ens]}} for ens in colors],
                }
            )
            parent.heatmap_plot.update_layout(_layout)
            return parent.correlation_plot.repr, parent.heatmap_plot

    @app.callback(
        Output(
            {"id": parent.uuid("response-overview"), "type": parent.uuid("graph")},
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
        _, __, ___, ____, responses, ensembles, corr_xindex, corr_param_resp
    ):
        if not (ensembles and responses and corr_param_resp["response"] in responses):
            raise PreventUpdate

        selected_response = corr_param_resp["response"]
        _plots = []
        _obs_plots = []

        for ensemble_id, data in ensembles.items():
            ensemble = load_ensemble(parent, ensemble_id)
            response = ensemble.responses[selected_response]
            x_axis = response.axis
            if str(x_axis[0]).isnumeric():
                style = deepcopy(assets.ERTSTYLE["response-plot"]["response-index"])
            else:
                style = deepcopy(assets.ERTSTYLE["response-plot"]["response"])
            data_df = response.data_df().copy()

            style.update({"marker": {"color": data["color"]}})
            style.update({"line": {"color": data["color"]}})
            _plots += [
                PlotModel(
                    x_axis=x_axis,
                    y_axis=data_df[realization],
                    text=realization,
                    name=realization,
                    **style,
                )
                for realization in data_df
            ]

            for obs in response.observations:
                _obs_plots += _get_observation_plots(obs.data_df(), x_axis)

        fig = go.Figure()
        for plot in _plots:
            fig.add_trace(plot.repr)

        _layout = assets.ERTSTYLE["figure"]["layout"].copy()
        _layout.update(dict(showlegend=False))
        fig.update_layout(_layout)

        x_index = corr_xindex.get(selected_response, 0)
        fig.add_shape(
            type="line",
            x0=x_axis[x_index],
            y0=0,
            x1=x_axis[x_index],
            y1=1,
            yref="paper",
            line=dict(color="rgb(30, 30, 30)", dash="dash", width=3),
        )
        # draw observations on top
        for plot in _obs_plots:
            fig.add_trace(plot.repr)

        fig.update_layout(clickmode="event+select")
        return fig

    @app.callback(
        [
            Output(
                {
                    "id": parent.uuid("response-scatterplot"),
                    "type": parent.uuid("graph"),
                },
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
            State(parent.uuid("ensemble-selection-store"), "data"),
        ],
    )
    def update_response_parameter_scatterplot(
        corr_xindex,
        corr_param_resp,
        parameters,
        responses,
        ensembles,
    ):

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

        for ensemble_id, data in ensembles.items():
            ensemble = load_ensemble(parent, ensemble_id)
            y_data = ensemble.parameters[selected_parameter].data_df()
            response = ensemble.responses[selected_response]
            x_index = corr_xindex.get(selected_response, 0)
            x_data = response.data_df().iloc[x_index]
            style = deepcopy(assets.ERTSTYLE["response-plot"]["response-index"])
            style["marker"]["color"] = data["color"]
            _colors[str(ensemble)] = data["color"]
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
        res_text = ""
        for response in responses:
            x_axis = ensemble.responses[response].axis
            x_value = x_axis[corr_xindex.get(response, 0)]
            if response == selected_response:
                res_text += f"**{response} @ {x_value}**, "
            else:
                res_text += f"{response} @ {x_value}, "
        res_text = [dcc.Markdown(res_text)]
        res_text += [dcc.Markdown(f"parameter: **{corr_param_resp['parameter']}**")]
        return fig, html.Div(res_text)

    @app.callback(
        Output(parent.uuid("correlation-store-xindex"), "data"),
        [
            Input(
                {"id": parent.uuid("response-overview"), "type": parent.uuid("graph")},
                "clickData",
            ),
            Input(parent.uuid("parameter-selection-store-resp"), "data"),
        ],
        [
            State(parent.uuid("correlation-store-xindex"), "data"),
            State(parent.uuid("correlation-store-selection"), "data"),
        ],
    )
    def update_corr_index(click_data, responses, corr_xindex, corr_param_resp):
        if not responses:
            raise PreventUpdate

        ctx = dash.callback_context
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if triggered_id == parent.uuid("parameter-selection-store-resp"):
            return {response: corr_xindex.get(response, 0) for response in responses}
        if click_data:
            corr_xindex[corr_param_resp["response"]] = click_data["points"][0][
                "pointIndex"
            ]
        return corr_xindex

    @app.callback(
        Output(parent.uuid("correlation-store-selection"), "data"),
        [
            Input(
                {
                    "id": parent.uuid("response-heatmap"),
                    "type": parent.uuid("graph"),
                },
                "clickData",
            ),
            Input(parent.uuid("parameter-selection-store-resp"), "data"),
            Input(parent.uuid("parameter-selection-store-param"), "data"),
        ],
        [
            State(parent.uuid("correlation-store-selection"), "data"),
        ],
    )
    def update_corr_param_resp(click_data, responses, parameters, corr_param_resp):
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
        return corr_param_resp
