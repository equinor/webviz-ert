import dash
import pandas as pd
import plotly.graph_objects as go

from copy import deepcopy
from typing import List, Dict, Union, Optional, Mapping
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from webviz_ert.controllers.controller_functions import response_options
from webviz_ert.plugins._webviz_ert import WebvizErtPluginABC
from webviz_ert.models import (
    ResponsePlotModel,
    BoxPlotModel,
    Response,
    MultiHistogramPlotModel,
    load_ensemble,
)
from webviz_ert import assets


def _get_univariate_misfits_boxplots(
    misfits_df: Optional[pd.DataFrame], color: str
) -> List[BoxPlotModel]:
    if misfits_df is None:
        return []
    x_axis = misfits_df.columns
    misfits_data = list()
    for misfits in misfits_df:
        plot = BoxPlotModel(
            y_axis=misfits_df[misfits].abs().values,
            name=f"{misfits}",
            color=color,
        )
        misfits_data.append(plot)
    return misfits_data


def _create_misfits_plot(
    response: Response, selected_realizations: List[int], color: str
) -> ResponsePlotModel:

    realizations = _get_univariate_misfits_boxplots(
        response.univariate_misfits_df(selected_realizations),
        color=color,
    )
    ensemble_plot = ResponsePlotModel(
        realizations,
        [],
        dict(
            hovermode="closest",
            uirevision=True,
        ),
    )
    return ensemble_plot


def observation_response_controller(parent: WebvizErtPluginABC, app: dash.Dash) -> None:
    @app.callback(
        Output(parent.uuid("response-selector"), "options"),
        [Input(parent.uuid("selected-ensemble-dropdown"), "value")],
    )
    def set_response_options(selected_ensembles: List[str]) -> List[Dict]:
        if not selected_ensembles:
            raise PreventUpdate
        ensembles = [
            load_ensemble(parent, ensemble_id) for ensemble_id in selected_ensembles
        ]
        return response_options(response_filters=["obs"], ensembles=ensembles)

    @app.callback(
        Output(parent.uuid("response-selector"), "value"),
        [Input(parent.uuid("response-selector"), "options")],
        [State(parent.uuid("response-selector"), "value")],
    )
    def set_responses_value(
        available_options: List[Dict], previous_selected_response: str
    ) -> str:
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
        [State(parent.uuid("selected-ensemble-dropdown"), "value")],
    )
    def update_graph(
        response: Optional[str],
        yaxis_type: List[str],
        misfits_type: str,
        selected_ensembles: List[str],
    ) -> go.Figure:
        if not response or response == "" or not selected_ensembles:
            raise PreventUpdate

        if misfits_type == "Summary":
            data_dict = {}
            colors = {}
            for index, ensemble_id in enumerate(selected_ensembles):
                ensemble = load_ensemble(parent, ensemble_id)
                summary_df = ensemble.responses[response].summary_misfits_df(
                    selection=None
                )  # What about selections?
                if summary_df is not None:
                    data_dict[ensemble.name] = summary_df
                colors[ensemble.name] = assets.get_color(index=index)
            if data_dict:
                plot = MultiHistogramPlotModel(
                    data_dict,
                    names={name: name for name in data_dict},
                    colors=colors,
                    hist=True,
                    kde=False,
                )
                return plot.repr

        def _generate_plot(ensemble_id: str, color: str) -> ResponsePlotModel:
            ensemble = load_ensemble(parent, ensemble_id)
            plot = _create_misfits_plot(ensemble.responses[response], [], color)
            return plot

        response_plots = [
            _generate_plot(ensemble_id, assets.get_color(index=index))
            for index, ensemble_id in enumerate(selected_ensembles)
        ]

        fig = go.Figure()
        for plt in response_plots:
            for trace in plt.repr.data:
                fig.add_trace(trace)
        fig.update_yaxes(type=yaxis_type)
        return fig
