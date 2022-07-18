import pytest
import pandas as pd
from webviz_ert.plugins._response_correlation import ResponseCorrelation
from webviz_ert.controllers.response_correlation_controller import (
    _get_first_observation_x,
    _define_style_ensemble,
)
from tests.conftest import (
    setup_plugin,
    select_by_name,
    select_ensemble,
    wait_a_bit,
    get_options,
)


def test_response_correlation_view(
    mock_data,
    dash_duo,
):
    plugin = setup_plugin(dash_duo, __name__, ResponseCorrelation)

    select_ensemble(dash_duo, plugin)

    resp_select = dash_duo.find_element(
        "#" + plugin.uuid("parameter-selector-multi-resp")
    )

    x, y = (0.5, 0.1)
    dash_duo.click_at_coord_fractions(resp_select, x, y)

    param_select = dash_duo.find_element(
        "#" + plugin.uuid("parameter-selector-multi-param")
    )
    param_select.click()

    x, y = (0.5, 0.1)
    # double click's for the sake if other parameter comes first
    dash_duo.click_at_coord_fractions(param_select, x, y)

    response_views = dash_duo.find_elements(".ert-view-cell")
    assert len(response_views) == 4

    # assert dash_duo.get_logs() == [], "browser console should contain no error"


def test_response_selector_sorting(mock_data, dash_duo):
    plugin = setup_plugin(dash_duo, __name__, ResponseCorrelation)
    wanted_ensemble_name = "nr_42"
    select_ensemble(dash_duo, plugin, wanted_ensemble_name)

    response_selector_container = dash_duo.find_element(
        "#" + plugin.uuid("container-parameter-selector-multi-resp")
    )
    response_list = response_selector_container.text.split("\n")

    assert response_list[0] == "test_response"
    assert response_list[1] == "test_response_4"
    assert response_list[2] == "test_response_44"
    assert response_list[3] == "test_response_99"


def test_axes_labels(mock_data, dash_duo):
    """test_axis_labels loads two different plots and checks that axes are
    labelled correctly"""

    plugin = setup_plugin(
        dash_duo, __name__, ResponseCorrelation, window_size=(1024, 2048)
    )

    # find the right ensemble which has mock data prepared for this test
    wanted_ensemble_name = "default3"
    select_ensemble(dash_duo, plugin, wanted_ensemble_name)

    wanted_responses = ["FGPT", "FOPR"]

    # we only see one response at a time, so we choose and check one after the
    # other
    for wanted_response in wanted_responses:

        response_selector_id = plugin.uuid("parameter-selector-multi-resp")
        select_by_name(dash_duo, f"#{response_selector_id}", wanted_response)

        # wait a bit for the graph to be drawn
        wait_a_bit(dash_duo)

        plot_id = plugin.uuid("response-overview")

        # check that y axis label spells out "Value"
        y_axis_title = dash_duo.find_element(f"#{plot_id} text.ytitle")
        assert y_axis_title.text == "Value"

        # check that one has date, the other has index as x axis label
        x_axis_title = dash_duo.find_element(f"#{plot_id} text.xtitle")
        if wanted_response == "FOPR":
            assert x_axis_title.text == "Date"
        else:
            assert x_axis_title.text == "Index"

        # clear response selection so next selection can be displayed
        response_deactivator_id = plugin.uuid("parameter-deactivator-resp")
        selected_response_closer = dash_duo.find_element(
            f"#{response_deactivator_id} .Select-value-icon"
        )
        selected_response_closer.click()

        # wait for deselected option to reappear among available options
        dash_duo.wait_for_contains_text(f"#{response_selector_id}", wanted_response)

    # assert dash_duo.get_logs() == [], "browser console should contain no error"


@pytest.mark.parametrize("input", [True, False])
def test_displaying_beta_warning(input: bool, dash_duo):
    plugin = setup_plugin(dash_duo, __name__, ResponseCorrelation, beta=input)
    beta_warning_element = dash_duo.find_element("#" + plugin.uuid("beta-warning"))
    assert beta_warning_element.is_displayed() == input


def test_show_respo_with_obs(mock_data, dash_duo):
    """Test response observation filter works as expected"""
    plugin = setup_plugin(dash_duo, __name__, ResponseCorrelation)

    select_ensemble(dash_duo, plugin, "default3")

    resp_selector_id = plugin.uuid("parameter-selector-multi-resp")
    default_responses = get_options(dash_duo, "#" + resp_selector_id)

    expected_def_responses = ["FGPT", "FOPR", "SNAKE_OIL_GPR_DIFF", "WOPR:OP1"]
    assert default_responses == expected_def_responses

    expected_obs_responses = ["FOPR", "WOPR:OP1"]
    obs_radio_btn = dash_duo.find_element(
        "#" + plugin.uuid("response-observations-check")
    )
    obs_radio_btn.click()
    obs_responses = get_options(dash_duo, "#" + resp_selector_id)
    assert obs_responses == expected_obs_responses


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


@pytest.mark.parametrize(
    "index,expected_color", [(0, "rgba(56,108,176,0.8)"), (1, "rgba(127,201,127,0.8)")]
)
def test_define_style_ensemble_color(index, expected_color):
    x_axis = pd.DataFrame([1])
    style = _define_style_ensemble(index, x_axis)
    assert style["line"]["color"] == expected_color
    assert style["marker"]["color"] == expected_color


@pytest.mark.parametrize(
    "x_axis_element,expected_mode",
    [
        ([pd._libs.tslibs.timestamps.Timestamp("01-01-2020")], "markers+lines"),
        ([str(1)], "markers"),
    ],
)
def test_define_style_ensemble_mode(x_axis_element, expected_mode):
    x_axis = pd.Index(x_axis_element)
    style = _define_style_ensemble(0, x_axis)
    assert style["mode"] == expected_mode
