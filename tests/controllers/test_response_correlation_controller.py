import pandas as pd
import pytest
from webviz_ert.controllers.response_correlation_controller import (
    _get_first_observation_x,
    _define_style_ensemble,
    _update_corr_index_dict,
    _layout_figure,
)

from webviz_ert.controllers.response_correlation_controller import (
    sort_dataframe,
)


def test_sort_dataframe():
    one_key = "WOPR"
    other_key = "BGMC"
    data = {}
    data[one_key] = [-0.4, 0.6, 0.2]
    data[other_key] = [0.3, 0.8, -0.1]
    dataframe = pd.DataFrame(data=data)
    index = None
    sorted_dataframe, _ = sort_dataframe(dataframe, index, other_key)
    assert list(sorted_dataframe[other_key]) == sorted(data[other_key])
    assert list(sorted_dataframe[one_key]) == [0.2, -0.4, 0.6]


@pytest.mark.parametrize(
    "index,expected_color", [(0, "rgba(56,108,176,0.8)"), (1, "rgba(127,201,127,0.8)")]
)
def test_define_style_ensemble_color(index, expected_color):
    x_axis = pd.DataFrame([1])
    style = _define_style_ensemble(index, x_axis)
    assert style["line"]["color"] == expected_color
    assert style["marker"]["color"] == expected_color


@pytest.mark.parametrize(
    "x_axis_list,expected_mode",
    [
        (
            [pd._libs.tslibs.timestamps.Timestamp("01-01-2020")],
            "markers+lines",
        ),
        ([str(1)], "markers"),
    ],
)
def test_define_style_ensemble_mode(x_axis_list, expected_mode):
    x_axis = pd.Index(x_axis_list)
    style = _define_style_ensemble(0, x_axis)
    assert style["mode"] == expected_mode


@pytest.mark.parametrize(
    "response_x_axis,observation_x_axis_list,expected_index",
    [
        (
            [
                "2020-01-01 00:00:00",
                "2020-01-07 00:00:00",
                "2020-01-14 00:00:00",
                "2020-01-21 00:00:00",
            ],
            [
                pd._libs.tslibs.timestamps.Timestamp("14-01-2020"),
                pd._libs.tslibs.timestamps.Timestamp("01-02-2020"),
            ],
            2,
        ),
        (pd.Index([0, 1]), [str(1)], 1),
    ],
)
def test_update_corr_index_dict(
    response_x_axis, observation_x_axis_list, expected_index
):
    observation_x_axis = pd.DataFrame(observation_x_axis_list, columns=["x_axis"])
    updated_index = _update_corr_index_dict(response_x_axis, observation_x_axis)
    assert expected_index == updated_index


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
    "observation,expected",
    [
        ([str(1)], int(1)),
        (
            [pd._libs.tslibs.timestamps.Timestamp("01-01-2020")],
            str("2020-01-01 00:00:00"),
        ),
    ],
)
def test_get_first_observation_x_valid(observation, expected):
    df_observation = pd.DataFrame(observation, columns=["x_axis"])
    result = _get_first_observation_x(df_observation)
    assert result == expected


def test_get_first_observation_x_invalid():
    df_observation = pd.DataFrame([int(1)], columns=["x_axis"])
    with pytest.raises(ValueError, match="invalid obs_data type"):
        _get_first_observation_x(df_observation)
