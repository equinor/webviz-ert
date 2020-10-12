import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from ertviz.data_loader import get_ensembles

# from ertviz.ert_client import get_response
from ertviz.models import EnsemblePlotModel, PlotModel
from ertviz.controllers import parse_url_query


def _get_realizations_data(realizations, x_axis):
    realizations_data = list()
    for realization in realizations:
        plot = PlotModel(
            x_axis=x_axis,
            y_axis=realization.data,
            text=realization.name,
            name=realization.name,
            mode="line",
            line=dict(color="royalblue"),
            marker=None,
        )
        realizations_data.append(plot)
    return realizations_data


def _get_observation_data(observation, x_axis):
    data = observation.values
    stds = observation.std
    x_axis_indexes = observation.data_indexes_as_axis
    x_axis = [x_axis[i] for i in x_axis_indexes]
    observation_data = PlotModel(
        x_axis=x_axis,
        y_axis=data,
        text="Observations",
        name="Observations",
        mode="markers",
        line=None,
        marker=dict(color="red", size=10),
    )
    lower_std_data = PlotModel(
        x_axis=x_axis,
        y_axis=[d - std for d, std in zip(data, stds)],
        text="Observations std lower",
        name="Observations std lower",
        mode="line",
        line=dict(color="red", dash="dash"),
        marker=None,
    )
    upper_std_data = PlotModel(
        x_axis=x_axis,
        y_axis=[d + std for d, std in zip(data, stds)],
        text="Observations std upper",
        name="Observations std upper",
        mode="line",
        line=dict(color="red", dash="dash"),
        marker=None,
    )
    return [observation_data, lower_std_data, upper_std_data]


def _create_response_model(url):
    response = get_response(url)

    x_axis = response.axis
    realizations = _get_realizations_data(response.realizations, x_axis)
    observations = []

    for obs in response.observations:
        observations += _get_observation_data(obs, x_axis)

    ensemble_plot = EnsemblePlotModel(
        realizations,
        observations,
        dict(
            xaxis={"title": "Index"},
            yaxis={"title": "Unit TODO"},
            margin={"l": 40, "b": 40, "t": 10, "r": 0},
            hovermode="closest",
            uirevision=True,
        ),
    )
    return ensemble_plot


def response_controller(parent, app):
    @app.callback(
        Output(parent.uuid("response-selector"), "options"), [Input("url", "search")]
    )
    def _set_response_options(query):
        queries = parse_url_query(query)
        if not "ensemble_id" in queries:
            return []
        ensemble_id = queries["ensemble_id"]
        names = get_ensembles()[eval(ensemble_id)].responses.name
        return [{"label": name, "value": name} for name in names]
        # ensemble_schema = get_ensemble(ensemble_id)

        # if "responses" in ensemble_schema:
        #     return [
        #         {"label": response["name"], "value": response["ref_url"]}
        #         for response in ensemble_schema["responses"]
        #     ]
        # return []

    @app.callback(
        Output(parent.uuid("response-selector"), "value"),
        [Input(parent.uuid("response-selector"), "options")],
    )
    def _set_responses_value(available_options):
        if available_options:
            return available_options[0]["value"]
        return ""

    @app.callback(
        Output(
            {"id": parent.uuid("response-graphic"), "type": parent.uuid("graph")},
            "figure",
        ),
        [
            Input(parent.uuid("response-selector"), "value"),
            Input(parent.uuid("selection-store"), "data"),
        ],
    )
    def _update_graph(response_url, selected_realizations):

        if response_url in [None, ""] and parent.ensemble_plot is None:
            raise PreventUpdate
        ctx = dash.callback_context

        if not ctx.triggered:
            raise PreventUpdate
        else:
            select_update = ctx.triggered[0]["prop_id"].split(".")[0] == parent.uuid(
                "selection-store"
            )

        if select_update:
            parent.ensemble_plot.selection = selected_realizations
        else:
            parent.ensemble_plot = _create_response_model(response_url)
        return parent.ensemble_plot.repr
