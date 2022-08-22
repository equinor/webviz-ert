from webviz_ert.plugins._response_correlation import ResponseCorrelation
from tests.conftest import (
    setup_plugin,
    select_by_name,
    select_ensemble,
    select_response,
    select_parameter,
)


def test_axes_labels(mock_data, dash_duo):
    """test_axis_labels loads two different plots and checks that axes are
    labelled correctly"""

    plugin = setup_plugin(
        dash_duo, __name__, ResponseCorrelation, window_size=(1024, 2048)
    )

    # find the right ensemble which has mock data prepared for this test
    wanted_ensemble_name = "default3"
    select_ensemble(dash_duo, plugin, wanted_ensemble_name)

    wanted_responses = ["WOPR:OP1", "FOPR"]

    # we only see one response at a time, so we choose and check one after the
    # other
    for wanted_response in wanted_responses:

        response_selector_id = plugin.uuid("parameter-selector-multi-resp")
        select_by_name(dash_duo, f"#{response_selector_id}", wanted_response)

        plot_id = plugin.uuid("response-overview")

        # check that y axis label spells out "Value"
        dash_duo.wait_for_text_to_equal(f"#{plot_id} text.ytitle", "Value")

        # check that one has date, the other has index as x axis label
        if wanted_response == "FOPR":
            dash_duo.wait_for_text_to_equal(f"#{plot_id} text.xtitle", "Date")
        else:
            dash_duo.wait_for_text_to_equal(f"#{plot_id} text.xtitle", "Index")

        # clear response selection so next selection can be displayed
        response_deactivator_id = plugin.uuid("parameter-deactivator-resp")
        selected_response_closer = dash_duo.find_element(
            f"#{response_deactivator_id} .Select-value-icon"
        )
        selected_response_closer.click()

        # wait for deselected option to reappear among available options
        dash_duo.wait_for_contains_text(f"#{response_selector_id}", wanted_response)

    # assert dash_duo.get_logs() == [], "browser console should contain no error"


def test_show_respo_with_obs(mock_data, dash_duo):
    """Test response observation filter works as expected"""
    plugin = setup_plugin(dash_duo, __name__, ResponseCorrelation)

    select_ensemble(dash_duo, plugin, "default3")

    expected_responses_with_observations = ["FOPR", "WOPR:OP1"]

    response_selector_id = "#" + plugin.uuid("parameter-selector-multi-resp")

    dash_duo.wait_for_text_to_equal(
        response_selector_id, "\n".join(expected_responses_with_observations)
    )


def test_info_text_appears_as_expected(
    mock_data,
    dash_duo,
):
    ensemble = "default3"
    response = "FOPR"
    parameter = "BPR_138_PERSISTENCE"
    index = "2010-01-10"
    plugin = setup_plugin(dash_duo, __name__, ResponseCorrelation)
    select_ensemble(dash_duo, plugin, ensemble)
    select_response(dash_duo, plugin, response, wait_for_plot=False)
    select_parameter(dash_duo, plugin, parameter, wait_for_plot=False)
    info_text_selector = f"#{plugin.uuid('info-text')}"
    expected_text = "".join(
        [f"RESPONSE: {response}", f"INDEX: {index}", f"PARAMETER: {parameter}"]
    )
    dash_duo.wait_for_text_to_equal(info_text_selector, expected_text)

    # assert dash_duo.get_logs() == [], "browser console should contain no error"
