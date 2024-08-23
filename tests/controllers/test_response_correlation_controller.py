import pandas as pd
import pytest
from webviz_ert.controllers.response_correlation_controller import (
    _define_style_ensemble,
    _format_index_text,
    _format_index_value,
    _get_selected_indexes,
    _layout_figure,
    _sort_dataframe,
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
            [pd.Timestamp("01-01-2020")],
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
    "raw_value,expected_formatted_value",
    [
        ("2022-08-05 14:25:00", "2022-08-05"),
        ("2022-09-21 14:25:00", "2022-09-21"),
        (14, "14"),
        ("213", "213"),
        ("SPAM", "SPAM"),
    ],
    ids=["date1", "date2", "numeric", "numeric-as-string", "silly-string"],
)
def test_format_index_text(raw_value: str, expected_formatted_value: str):
    assert _format_index_text(raw_value) == expected_formatted_value


@pytest.mark.parametrize(
    "raw_value,expected_formatted_value",
    [
        ("2022-08-05 14:25:00", "2022-08-05 14:25:00"),
        ("2022-09-21 14:25:00", "2022-09-21 14:25:00"),
        (14, 14),
        ("213", 213),
        ("SPAM", "SPAM"),
    ],
    ids=["date1", "date2", "numeric", "numeric-as-string", "silly-string"],
)
def test_format_index_value(raw_value: str, expected_formatted_value: str):
    assert _format_index_value(raw_value) == expected_formatted_value


@pytest.mark.parametrize(
    "plots, date_ranges, expected",
    [
        ([], None, {}),
        ([], {}, {}),
        ([], {}, {}),
        (
            [
                PlotModel(
                    x_axis=[0, 5, 10], y_axis=[1, 1, 1], name="plot1", **PLOT_STYLE
                )
            ],
            {"x": ["2020-01-01", "2020-01-03"]},
            {},
        ),
        (
            [
                PlotModel(
                    x_axis=[0, 5, 10], y_axis=[1, 1, 1], name="plot1", **PLOT_STYLE
                )
            ],
            {"x2": [1, 3]},
            {},
        ),
        (
            [
                PlotModel(
                    x_axis=[0, 5, 10], y_axis=[1, 1, 1], name="plot1", **PLOT_STYLE
                ),
                PlotModel(
                    x_axis=[pd.Timestamp("2020-01-02")],
                    y_axis=[1, 1, 1],
                    name="plot2",
                    **PLOT_STYLE,
                ),
            ],
            {"x": ["2020-01-01", "2020-01-03"]},
            {"plot2": [pd.Timestamp("2020-01-02")]},
        ),
        (
            [
                PlotModel(
                    x_axis=[0, 5, 10], y_axis=[1, 1, 1], name="plot1", **PLOT_STYLE
                ),
                PlotModel(
                    x_axis=[pd.Timestamp("2020-01-02")],
                    y_axis=[1, 1, 1],
                    name="plot2",
                    **PLOT_STYLE,
                ),
            ],
            {"x": ["2020-01-01", "2020-01-03"], "x2": [4, 6]},
            {"plot1": [5], "plot2": [pd.Timestamp("2020-01-02")]},
        ),
    ],
)
def test_get_selected_indexes(plots, date_ranges, expected):
    assert _get_selected_indexes(plots, date_ranges) == expected
