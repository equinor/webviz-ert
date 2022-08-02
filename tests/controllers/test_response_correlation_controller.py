import pandas as pd
import pytest

from pandas._libs.tslibs.timestamps import Timestamp

from webviz_ert.controllers.response_correlation_controller import (
    _define_style_ensemble,
    _layout_figure,
)

from webviz_ert.controllers.response_correlation_controller import (
    _sort_dataframe,
    _get_selected_indexes,
    _get_x_range_obs,
    _layout_obs_selector,
)
from webviz_ert.models import PlotModel


PLOT_STYLE = {
    "mode": "markers",
    "line": None,
    "marker": {"color": "rgba(56,108,176,0.8)", "size": 9},
    "text": "NA",
}


def test_sort_dataframe():
    one_key = "WOPR"
    other_key = "BGMC"
    data = {}
    data[one_key] = [-0.4, 0.6, 0.2]
    data[other_key] = [0.3, 0.8, -0.1]
    dataframe = pd.DataFrame(data=data)
    index = None
    sorted_dataframe, _ = _sort_dataframe(dataframe, index, other_key)
    assert list(sorted_dataframe[other_key]) == sorted(data[other_key])
    assert list(sorted_dataframe[one_key]) == [0.2, -0.4, 0.6]


@pytest.mark.parametrize(
    "index,expected_color", [(0, "rgba(56,108,176,0.8)"), (1, "rgba(127,201,127,0.8)")]
)
def test_define_style_ensemble_color(index, expected_color):
    x_axis = pd.Index([1])
    style = _define_style_ensemble(index, x_axis)
    assert style["line"]["color"] == expected_color
    assert style["marker"]["color"] == expected_color


@pytest.mark.parametrize(
    "x_axis_list,expected_mode",
    [
        (
            [Timestamp("01-01-2020")],
            "markers+lines",
        ),
        ([str(1)], "markers"),
    ],
)
def test_define_style_ensemble_mode(x_axis_list, expected_mode):
    x_axis = pd.Index(x_axis_list)
    style = _define_style_ensemble(0, x_axis)
    assert style["mode"] == expected_mode


def test_layout_figure():
    layout = _layout_figure(x_axis_label="Index")  # "Date" is also possible
    expected_layout = {
        "hovermode": "closest",
        "uirevision": True,
        "margin": {"l": 5, "b": 5, "t": 25, "r": 5},
        "autosize": True,
        "showlegend": False,
        "clickmode": "event+select",
        "xaxis": {"title": {"text": "Index"}},
        "yaxis": {"title": {"text": "Value"}},
    }

    assert layout == expected_layout


@pytest.mark.parametrize(
    "index_axis,keys_expected_in_layout",
    [(False, {"xaxis"}), (True, {"xaxis", "xaxis2"})],
)
def test_layout_obs_selector(index_axis, keys_expected_in_layout):
    layout = _layout_obs_selector(index_axis)
    assert keys_expected_in_layout <= layout.keys()


@pytest.mark.parametrize(
    "store_keys,index_axis,time_axis,expected_x_range",
    [
        (["x", "x2"], False, False, None),
        (
            ["x", "x2"],
            True,
            True,
            ["2012-07-01 00:00:00", "2012-12-01 00:00:00"],
        ),  # This state maybe bug ?
        (["x", "x2"], False, True, ["2012-07-01 00:00:00", "2012-12-01 00:00:00"]),
        (["x", "x2"], True, False, [100, 120]),
        (["x"], True, True, None),
        (["x"], False, False, None),
        (["x"], True, False, None),  # undefined, this state is not expected to happen
        (["x"], False, True, ["2012-07-01 00:00:00", "2012-12-01 00:00:00"]),
        (["x2"], False, False, None),
        (["x2"], True, True, None),
        (["x2"], True, True, None),  # undefined, this state is not expected to happen
        (["x2"], True, False, [100, 120]),
    ],
)
def test_get_x_range_obs(store_keys, index_axis, time_axis, expected_x_range):
    store_obs_range_full = {
        "x": ["2012-07-01 00:00:00", "2012-12-01 00:00:00"],
        "x2": [100, 120],
        "y": [-0.5, 2],
    }
    store_obs_range = {
        store_key: store_obs_range_full[store_key] for store_key in store_keys
    }
    x_range = _get_x_range_obs(store_obs_range, index_axis, time_axis)
    assert x_range == expected_x_range


@pytest.mark.parametrize(
    "plots, selected_data, expected",
    [
        ([], None, {}),
        ([], {}, {}),
        ([], {"range": {}}, {}),
        (
            [
                PlotModel(
                    x_axis=[0, 5, 10], y_axis=[1, 1, 1], name="plot1", **PLOT_STYLE
                )
            ],
            {"range": {"x": ["2020-01-01", "2020-01-03"]}},
            {"plot1": []},
        ),
        (
            [
                PlotModel(
                    x_axis=[0, 5, 10], y_axis=[1, 1, 1], name="plot1", **PLOT_STYLE
                )
            ],
            {"range": {"x2": [1, 3]}},
            {"plot1": []},
        ),
        (
            [
                PlotModel(
                    x_axis=[0, 5, 10], y_axis=[1, 1, 1], name="plot1", **PLOT_STYLE
                ),
                PlotModel(
                    x_axis=[Timestamp("2020-01-02")],
                    y_axis=[1, 1, 1],
                    name="plot2",
                    **PLOT_STYLE
                ),
            ],
            {"range": {"x": ["2020-01-01", "2020-01-03"]}},
            {"plot1": [], "plot2": [Timestamp("2020-01-02")]},
        ),
        (
            [
                PlotModel(
                    x_axis=[0, 5, 10], y_axis=[1, 1, 1], name="plot1", **PLOT_STYLE
                ),
                PlotModel(
                    x_axis=[Timestamp("2020-01-02")],
                    y_axis=[1, 1, 1],
                    name="plot2",
                    **PLOT_STYLE
                ),
            ],
            {"range": {"x": ["2020-01-01", "2020-01-03"], "x2": [4, 6]}},
            {"plot1": [5], "plot2": [Timestamp("2020-01-02")]},
        ),
    ],
)
def test_get_selected_indexes(plots, selected_data, expected):
    assert _get_selected_indexes(plots, selected_data) == expected
