import dash
import pandas as pd
import plotly.graph_objects as go

from copy import deepcopy
from typing import List, Dict, Union, Optional, Mapping, Any
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from webviz_ert.controllers.controller_functions import response_options
from webviz_ert.plugins import WebvizErtPluginABC
from webviz_ert.models import (
    ResponsePlotModel,
    BoxPlotModel,
    Response,
    MultiHistogramPlotModel,
    load_ensemble,
)
from webviz_ert import assets


def _get_univariate_misfits_boxplots(
    misfits_df: Optional[pd.DataFrame], ensemble_name: str, color: str
) -> List[BoxPlotModel]:
    if misfits_df is None:
        return []
    x_axis = misfits_df.columns
    realization_names = [f"Realization {name}" for name in misfits_df.index.values]
    misfit_plots = list()
    for misfits in misfits_df:
        plot = BoxPlotModel(
            y_axis=misfits_df[misfits].abs().values,
            name=misfits,
            ensemble_name=ensemble_name,
            color=color,
            customdata=realization_names,
            hovertemplate="(%{x}, %{y}) - %{customdata}",
        )
        misfit_plots.append(plot)
    return misfit_plots


def _create_misfits_plot(
    response: Response, selected_realizations: List[int], color: str, ensemble_name: str
) -> ResponsePlotModel:
    realizations = _get_univariate_misfits_boxplots(
        response.univariate_misfits_df(selected_realizations),
        ensemble_name=ensemble_name,
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
        [
            Output(parent.uuid("response-selector"), "options"),
            Output(parent.uuid("response-selector"), "value"),
            Output(parent.uuid("response-selector-store"), "data"),
        ],
        [
            Input(parent.uuid("selected-ensemble-dropdown"), "value"),
            Input(parent.uuid("response-selector"), "value"),
        ],
        [
            State(parent.uuid("response-selector-store"), "data"),
        ],
    )
    def set_response_callback(
        selected_ensembles: List[str],
        selected_resp: Optional[str],
        selected_resp_store: Optional[str],
    ) -> List[Any]:
        ctx = dash.callback_context
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if not triggered_id:
            raise PreventUpdate

        if triggered_id == parent.uuid("response-selector"):
            selected_resp_store = selected_resp

        ensembles = [
            load_ensemble(parent, ensemble_id) for ensemble_id in selected_ensembles
        ]
        responses = response_options(response_filters=["obs"], ensembles=ensembles)
        options = [{"label": name, "value": name} for name in sorted(responses)]

        if options:
            selected_resp = selected_resp_store
        else:
            selected_resp = None
            selected_resp_store = None

        parent.save_state("response", selected_resp_store)

        return [options, selected_resp, selected_resp_store]

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
            return go.Figure()

        if misfits_type == "Summary":
            data_dict = {}
            colors = {}
            for index, ensemble_id in enumerate(selected_ensembles):
                ensemble = load_ensemble(parent, ensemble_id)
                summary_df = ensemble.responses[response].summary_misfits_df(
                    selection=None
                )  # What about selections?
                if summary_df is not None:
                    data_dict[ensemble.name] = summary_df.transpose()
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
            resp = ensemble.responses[str(response)]
            plot = _create_misfits_plot(resp, [], color, ensemble.name)
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
