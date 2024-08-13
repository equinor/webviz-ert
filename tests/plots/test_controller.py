import pandas as pd
import numpy as np
from webviz_ert.controllers.multi_response_controller import (
    _get_observation_plots,
    _get_realizations_plots,
    _get_realizations_statistics_plots,
)
from webviz_ert.controllers.observation_response_controller import (
    _get_univariate_misfits_boxplots,
)

from webviz_ert.data_loader import get_ensembles
from webviz_ert.models import EnsembleModel, PriorModel
from webviz_ert.models import (
    HistogramPlotModel,
    MultiHistogramPlotModel,
    BoxPlotModel,
    ParallelCoordinatesPlotModel,
    BarChartPlotModel,
)
import webviz_ert.assets as assets


def test_observation_plot_representation():
    observation_df = pd.DataFrame(
        data={
            "values": [2.85325093, 7.20311703, 21.38648991, 31.51455593, 53.56766604],
            "std": [0.1, 1.1, 4.1, 9.1, 16.1],
            "x_axis": [0, 2, 4, 6, 8],
            "attributes": "Key1 Value1<br>Key2 Value2<br>",
            "active": [True, False, True, False, False],
        }
    )

    plot = _get_observation_plots(observation_df)

    assert "mode" in plot.repr

    np.testing.assert_equal(observation_df["x_axis"].values, plot.repr.x)
    assert len(plot.repr.y) == len(observation_df)

    np.testing.assert_equal(plot.repr.y, observation_df["values"].values)
    np.testing.assert_equal(plot.repr.error_y.array, observation_df["std"].values)
    np.testing.assert_equal(plot.repr.text, observation_df["attributes"].values)
    np.testing.assert_equal(
        plot.repr.marker.color,
        (
            "rgb(176, 28, 52)",
            "rgb(0, 0, 0)",
            "rgb(176, 28, 52)",
            "rgb(0, 0, 0)",
            "rgb(0, 0, 0)",
        ),
    )


def test_realizations_plot_representation():
    data = np.random.rand(200).reshape(-1, 20)
    realization_df = pd.DataFrame(data=data, index=range(10), columns=range(20))
    x_axis = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    plots = _get_realizations_plots(
        realization_df, x_axis, assets.ERTSTYLE["ensemble-selector"]["color_wheel"][0]
    )
    assert len(plots) == 20
    for idx, plot in enumerate(plots):
        np.testing.assert_equal(x_axis, plot.repr.x)
        np.testing.assert_equal(plot.repr.y, realization_df[idx].values)


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
    name_dict = {}
    colors_dict = {}

    ensemble_names = ["default", "update_1", "update_2"]
    colors = assets.ERTSTYLE["ensemble-selector"]["color_wheel"]
    for ensemble_date, (ensemble_name, color) in enumerate(
        zip(ensemble_names, colors[: len(ensemble_names)])
    ):
        key = f"{ensemble_date}, {ensemble_name}"
        data = np.random.rand(20).reshape(-1, 20)
        data_df = pd.DataFrame(data=data, index=range(1), columns=range(20))
        data_df.index.name = "KEY_NAME"
        data_dict[key] = data_df
        name_dict[key] = f"{ensemble_name}"
        colors_dict[key] = color
    priors = {
        (0, "default"): (PriorModel("uniform", ["std", "mean"], [0, 1]), colors[0])
    }

    plot = MultiHistogramPlotModel(
        data_dict, name_dict, colors_dict, hist=True, kde=False
    )
    assert plot.bin_count == 4

    plot = MultiHistogramPlotModel(
        data_dict,
        name_dict,
        colors_dict,
        hist=True,
        kde=False,
        priors=priors,
        bin_count=10,
    )
    assert plot.bin_count == 10
    plot = plot.repr
    for idx, ensemble_name in enumerate(ensemble_names):
        key = f"{idx}, {ensemble_name}"
        np.testing.assert_equal(plot.data[idx].x, data_dict[key].values.flatten())
        assert plot.data[idx].histnorm == "probability density"
        assert plot.data[idx].autobinx == False
        assert plot.data[idx].marker.color == colors_dict[key]
        assert plot.data[idx].name == ensemble_name

    assert plot.data[-1].name == "(0, 'default')-prior"


def test_parallel_coordinates_representation():
    data_dict = {}
    colors_dict = {}

    ensemble_names = ["default", "update_1", "update_2"]
    colors = assets.ERTSTYLE["ensemble-selector"]["color_wheel"]
    for idx, (ensemble_name, color) in enumerate(
        zip(ensemble_names, colors[: len(ensemble_names)])
    ):
        key = f"{idx}, {ensemble_name}"
        data = np.random.rand(50).reshape(-1, 5)
        data_df = pd.DataFrame(data=data, columns=[f"PARAM_{i}" for i in range(5)])
        data_df["ensemble_id"] = idx
        data_dict[key] = data_df
        colors_dict[key] = color

    plot = ParallelCoordinatesPlotModel(data_dict, colors_dict)
    plot = plot.repr

    assert len(plot.data[0].dimensions) == 5
    for idx, ensemble_name in enumerate(ensemble_names):
        key = f"{idx}, {ensemble_name}"
        assert plot.data[0].dimensions[idx].label == f"PARAM_{idx}"
        assert len(plot.data[0].dimensions[idx].values) == 10 * len(ensemble_names)
        assert plot.data[0].labelangle == 45
        assert len(plot.data[0].line.color) == 10 * len(ensemble_names)


def test_univariate_misfits_boxplot_representation():
    data = np.random.rand(200).reshape(-1, 20)
    missfits_df = pd.DataFrame(data=data, index=range(10), columns=range(20))
    ensemble_name = "test-ensemble"
    plots = _get_univariate_misfits_boxplots(
        missfits_df.copy(), ensemble_name=ensemble_name, color="rgb(255,0,0)"
    )
    assert len(plots) == 20
    for id_plot, plot in enumerate(plots):
        np.testing.assert_equal(0.3, plot.repr.jitter)
        np.testing.assert_equal("all", plot.repr.boxpoints)
        x_pos = missfits_df.columns[id_plot]
        if isinstance(x_pos, int):
            name = f"Value {x_pos}"
        else:
            name = f"{x_pos} - {ensemble_name}"
        assert name == plot.repr.name


def test_boxplot_representation():
    data = np.random.rand(10)
    data_df = pd.DataFrame(data=data, index=range(10))

    plot = BoxPlotModel(
        y_axis=data_df.values,
        name="Boxplot@Location5",
        color=assets.ERTSTYLE["ensemble-selector"]["color_wheel"][0],
    )
    plot = plot.repr
    np.testing.assert_equal(plot.y.flatten(), data)
    assert plot.boxpoints == "all"
    assert plot.name == "Boxplot@Location5"


def test_barchart_representation():
    data_dict = {}
    colors_dict = {}

    ensemble_names = ["default", "update_1", "update_2"]
    colors = assets.ERTSTYLE["ensemble-selector"]["color_wheel"]
    param_num = 5
    for idx, (ensemble_name, color) in enumerate(
        zip(ensemble_names, colors[: len(ensemble_names)])
    ):
        key = f"{idx}, {ensemble_name}"
        data = np.random.rand(param_num)
        data_df = pd.DataFrame(
            data=data, index=[f"PARAM_{i}" for i in range(param_num)]
        )
        data_dict[key] = data_df
        colors_dict[key] = color

    plot = BarChartPlotModel(data_dict, colors_dict)
    plot = plot.repr

    for idx, ensemble_name in enumerate(ensemble_names):
        key = f"{idx}, {ensemble_name}"
        assert plot.data[idx].name == key
        np.testing.assert_equal(
            plot.data[idx].y, [f"PARAM_{i}" for i in range(param_num)]
        )
        assert plot.data[idx].orientation == "h"
        assert plot.data[idx].x.shape == (param_num, 1)
        assert plot.data[idx].marker.color == colors[idx]
