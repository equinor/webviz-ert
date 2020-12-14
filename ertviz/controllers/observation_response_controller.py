import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from copy import deepcopy
from ertviz.models import (
    ResponsePlotModel,
    BoxPlotModel,
    EnsembleModel,
    MultiHistogramPlotModel,
)


def _get_univariate_misfits_boxplots(misfits_df, color):
    if misfits_df is None:
        return []

    x_axis = misfits_df.pop("x_axis")
    misfits_data = list()
    for misfits in misfits_df.T:
        plot = BoxPlotModel(
            y_axis=misfits_df.T[misfits].values,
            name=f"Misfits@{int(x_axis.loc[misfits])}",
            color=color,
        )
        misfits_data.append(plot)
    return misfits_data


def _create_misfits_plot(response, selected_realizations, color):

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


def observation_response_controller(parent, app):
    @app.callback(
        Output(parent.uuid("response-selector"), "options"),
        [Input(parent.uuid("ensemble-selection-store"), "data")],
    )
    def _set_response_options(selected_ensembles):
        if not selected_ensembles:
            raise PreventUpdate
        ensemble_id, _ = selected_ensembles.popitem()
        ensemble = parent.ensembles.get(
            ensemble_id,
            EnsembleModel(ref_url=ensemble_id, project_id=parent.project_identifier),
        )
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

        if misfits_type == "Summary":
            data_dict = {}
            colors = {}
            for ensemble_id, color in selected_ensembles.items():
                ensemble = parent.ensembles.get(ensemble_id, None)
                summary_df = ensemble.responses[response].summary_misfits_df(
                    selection=None
                )  # What about selections?
                if summary_df is not None:
                    data_dict[parent.ensembles[ensemble_id]._name] = summary_df
                colors[parent.ensembles[ensemble_id]._name] = color["color"]
            if bool(data_dict):
                plot = MultiHistogramPlotModel(
                    data_dict,
                    colors=colors,
                    hist=True,
                    kde=False,
                )
                return plot.repr

        def _generate_plot(ensemble_id, color):
            ensemble = parent.ensembles.get(ensemble_id, None)
            plot = _create_misfits_plot(ensemble.responses[response], None, color)
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
