import pandas as pd
import numpy as np
from unittest import mock
from tests.conftest import mocked_get_info, mocked_requests_get
from ertviz.controllers.multi_response_controller import (
    _get_observation_plots,
    _get_realizations_plots,
    _get_realizations_statistics_plots,
)
from ertviz.controllers.ensemble_selector_controller import _construct_graph
from ertviz.data_loader import get_ensembles
from ertviz.models import EnsembleModel
from ertviz.models import HistogramPlotModel, MultiHistogramPlotModel
import ertviz.assets as assets


def test_observation_plot_representation():
    observation_df = pd.DataFrame(
        data={
            "values": [2.85325093, 7.20311703, 21.38648991, 31.51455593, 53.56766604],
            "std": [0.1, 1.1, 4.1, 9.1, 16.1],
            "x_axis": [0, 2, 4, 6, 8],
        }
    )
    x_axis = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    plots = _get_observation_plots(observation_df, x_axis)

    assert len(plots) == 1
    assert "mode" in plots[0].repr
    for plot in plots:
        np.testing.assert_equal(observation_df["x_axis"].values, plot.repr.x)
        assert len(plot.repr.y) == len(observation_df)

    np.testing.assert_equal(plots[0].repr.y, observation_df["values"].values)
    np.testing.assert_equal(plots[0].repr.error_y.array, observation_df["std"].values)


def test_realizations_plot_representation():
    data = np.random.rand(200).reshape(-1, 20)
    realization_df = pd.DataFrame(data=data, index=range(10), columns=range(20))
    x_axis = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    plots = _get_realizations_plots(
        realization_df, x_axis, assets.ERTSTYLE["ensemble-selector"]["color_wheel"][0]
    )
    assert len(plots) == 20
    for plot in plots:
        np.testing.assert_equal(x_axis, plot.repr.x)
        np.testing.assert_equal(plot.repr.y, realization_df[plot.name].values)


def test_realizations_statistics_plot_representation():
    data = np.random.rand(200).reshape(-1, 20)
    realization_df = pd.DataFrame(data=data, index=range(10), columns=range(20))
    x_axis = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    plots = _get_realizations_statistics_plots(
        realization_df, x_axis, assets.ERTSTYLE["ensemble-selector"]["color_wheel"][0]
    )

    assert len(plots) == 3
    assert "mode" in plots[0].repr
    for plot in plots:
        np.testing.assert_equal(x_axis, plot.repr.x)

    np.testing.assert_equal(plots[0].repr.y, np.mean(data, axis=1))
    np.testing.assert_equal(plots[1].repr.y, np.quantile(data, 0.1, axis=1))
    np.testing.assert_equal(plots[2].repr.y, np.quantile(data, 0.9, axis=1))


@mock.patch("ertviz.data_loader.requests.get", side_effect=mocked_requests_get)
@mock.patch("ertviz.data_loader.get_info", side_effect=mocked_get_info)
def test_ensemble_selector_graph_constructor(mock_request, mock_get_info):
    ensemble_dict = get_ensembles()
    ensemble_models = {
        schema["ref_url"]: EnsembleModel(schema["ref_url"]) for schema in ensemble_dict
    }
    graph_data = _construct_graph(ensemble_models)
    parent_ensemble_node = {
        "data": {"id": "http://127.0.0.1:5000/ensembles/1", "label": "default"}
    }
    parent_child_edge = {
        "data": {
            "source": "http://127.0.0.1:5000/ensembles/1",
            "target": "http://127.0.0.1:5000/ensembles/2",
        }
    }
    assert parent_ensemble_node in graph_data
    assert parent_child_edge in graph_data


def test_histogram_plot_representation():
    data = np.random.rand(20).reshape(-1, 20)
    data_df = pd.DataFrame(data=data, index=range(1), columns=range(20))
    data_df.index.name = "key_name"

    plot = HistogramPlotModel(data_df, hist=True, kde=False)
    plot.selection = range(5)
    plot = plot.repr
    np.testing.assert_equal(plot.data[0].x, data.flatten()[:5])
    assert plot.data[0].histnorm == "probability density"
    assert plot.data[0].autobinx == False


def test_multi_histogram_plot_representation():
    data_dict = {}
    colors_dict = {}

    keys = "KEY_NAME"
    ensemble_names = ["default", "update_1", "update_2"]
    colors = assets.ERTSTYLE["ensemble-selector"]["color_wheel"]
    for ensemble_name, color in zip(ensemble_names, colors[: len(ensemble_names)]):
        data = np.random.rand(20).reshape(-1, 20)
        data_df = pd.DataFrame(data=data, index=range(1), columns=range(20))
        data_df.index.name = "KEY_NAME"
        data_dict[ensemble_name] = data_df
        colors_dict[ensemble_name] = color

    plot = MultiHistogramPlotModel(data_dict, colors_dict, hist=True, kde=False)
    plot = plot.repr
    for idx, ensemble_name in enumerate(ensemble_names):
        np.testing.assert_equal(
            plot.data[idx].x, data_dict[ensemble_name].values.flatten()
        )
        assert plot.data[idx].histnorm == "probability density"
        assert plot.data[idx].autobinx == False
        assert plot.data[idx].marker.color == colors_dict[ensemble_name]
        assert plot.data[idx].name == ensemble_name
