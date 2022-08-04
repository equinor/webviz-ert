import pytest
from webviz_ert.plugins._response_correlation import ResponseCorrelation
from tests.conftest import (
    setup_plugin,
    select_by_name,
    select_ensemble,
    select_parameter,
    select_response,
    wait_a_bit,
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

        plot_id = plugin.uuid("response-overview")

        # check that y axis label spells out "Value"
        dash_duo.wait_for_text_to_equal(f"#{plot_id} text.ytitle", "Value", timeout=5)

        # check that one has date, the other has index as x axis label
        if wanted_response == "FOPR":
            dash_duo.wait_for_text_to_equal(
                f"#{plot_id} text.xtitle", "Date", timeout=5
            )
        else:
            dash_duo.wait_for_text_to_equal(
                f"#{plot_id} text.xtitle", "Index", timeout=5
            )

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

    expected_default_responses = ["FGPT", "FOPR", "SNAKE_OIL_GPR_DIFF", "WOPR:OP1"]
    expected_responses_with_observations = ["FOPR", "WOPR:OP1"]

    response_selector_id = "#" + plugin.uuid("parameter-selector-multi-resp")

    dash_duo.wait_for_text_to_equal(
        response_selector_id, "\n".join(expected_default_responses)
    )

    obs_radio_btn = dash_duo.find_element(
        "#" + plugin.uuid("response-observations-check")
    )
    obs_radio_btn.click()

    dash_duo.wait_for_text_to_equal(
        response_selector_id, "\n".join(expected_responses_with_observations)
    )


def test_info_text_appears_as_expected(
    mock_data,
    dash_duo,
):
    response = "SNAKE_OIL_GPR_DIFF"
    parameter = "BPR_138_PERSISTENCE"
    index = "0"
    plugin = setup_plugin(dash_duo, __name__, ResponseCorrelation)
    select_ensemble(dash_duo, plugin)
    select_response(dash_duo, plugin, response, wait_for_it=False)
    select_parameter(dash_duo, plugin, parameter, wait_for_it=False)
    info_text_selector = f"#{plugin.uuid('info-text')}"
    expected_text = "".join(
        [f"RESPONSE: {response}", f"INDEX: {index}", f"PARAMETER: {parameter}"]
    )
    dash_duo.wait_for_text_to_equal(info_text_selector, expected_text)

    # assert dash_duo.get_logs() == [], "browser console should contain no error"
