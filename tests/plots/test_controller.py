import pandas as pd
import numpy as np
from ertviz.controllers.response_controller import (
    _get_observation_plots,
    _get_realizations_plots,
)
from ertviz.controllers.response_controller import _get_realizations_statistics_plots


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

    assert len(plots) == 3
    assert "mode" in plots[0].repr
    for plot in plots:
        np.testing.assert_equal(observation_df["x_axis"].values, plot.repr.x)
        assert len(plot.repr.y) == len(observation_df)

    np.testing.assert_equal(plots[0].repr.y, observation_df["values"].values)
    np.testing.assert_equal(
        plots[1].repr.y, (observation_df["values"] - observation_df["std"]).values
    )
    np.testing.assert_equal(
        plots[2].repr.y, (observation_df["values"] + observation_df["std"]).values
    )


def test_realizations_plot_representation():
    data = np.random.rand(200).reshape(-1, 20)
    realization_df = pd.DataFrame(data=data, index=range(10), columns=range(20))
    x_axis = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    plots = _get_realizations_plots(realization_df, x_axis)
    assert len(plots) == 20
    for plot in plots:
        np.testing.assert_equal(x_axis, plot.repr.x)
        np.testing.assert_equal(plot.repr.y, realization_df[plot.name].values)


def test_realizations_statistics_plot_representation():
    data = np.random.rand(200).reshape(-1, 20)
    realization_df = pd.DataFrame(data=data, index=range(10), columns=range(20))
    x_axis = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    plots = _get_realizations_statistics_plots(realization_df, x_axis)

    assert len(plots) == 3
    assert "mode" in plots[0].repr
    for plot in plots:
        np.testing.assert_equal(x_axis, plot.repr.x)

    np.testing.assert_equal(plots[0].repr.y, np.mean(data, axis=1))
    np.testing.assert_equal(plots[1].repr.y, np.quantile(data, 0.1, axis=1))
    np.testing.assert_equal(plots[2].repr.y, np.quantile(data, 0.9, axis=1))
