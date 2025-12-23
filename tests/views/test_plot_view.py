import pytest

from tests.conftest import (
    select_ensemble,
    select_parameter,
    select_response,
    setup_plugin,
    wait_a_bit,
)
from webviz_ert.plugins._response_comparison import ResponseComparison


@pytest.mark.browser_test
def test_plot_view(
    mock_data,
    dash_duo,
):
    # This test selects an ensemble from the ensemble-multi-selector
    # then selects a response and parameter and checks that the
    # DOM element for both are created.
    plugin = setup_plugin(dash_duo, __name__, ResponseComparison)

    select_ensemble(dash_duo, plugin)

    select_response(dash_duo, plugin, "SNAKE_OIL_GPR_DIFF@199")

    select_parameter(dash_duo, plugin, "BPR_138_PERSISTENCE")

    # assert dash_duo.get_logs() == [], "browser console should contain no error"


@pytest.mark.browser_test
def test_clearing_parameters_view(
    mock_data,
    dash_duo,
):
    # this is a regression test, ensuring that all appropriate plots are
    # cleared when a selection of multiple parameters is cleared.
    # we select an ensemble, select a response, select two parameters, check
    # that three graphs are present, clear all parameters, and check that just
    # the response graph remains
    plugin = setup_plugin(dash_duo, __name__, ResponseComparison)

    select_ensemble(dash_duo, plugin)

    response_name = "SNAKE_OIL_GPR_DIFF@199"

    # click the response, and check that the response graph appears
    select_response(dash_duo, plugin, response_name)

    # click some parameters
    select_parameter(dash_duo, plugin, "BPR_138_PERSISTENCE")
    select_parameter(dash_duo, plugin, "OP1_DIVERGENCE_SCALE")

    # clear parameter selection
    clear_all = dash_duo.find_element(
        "#" + plugin.uuid("parameter-deactivator-param") + " span.Select-clear-zone"
    )
    clear_all.click()

    # verify only expected response plot is left in place
    dash_duo.find_element(f'.dash-graph[id*="{response_name}"]')

    # assert dash_duo.get_logs() == [], "browser console sho uld contain no error"


@pytest.mark.browser_test
def test_clearing_ensembles_view(
    mock_data,
    dash_duo,
):
    # this is a regression test, ensuring that clearing all ensembles actually
    # removes all ensembles, all responses, all parameters, and all plots

    plugin = setup_plugin(dash_duo, __name__, ResponseComparison, (1024, 2048))

    # click and choose two ensembles
    select_ensemble(dash_duo, plugin)
    select_ensemble(dash_duo, plugin)

    # click the response, and check that the response graph appears
    select_response(dash_duo, plugin, "SNAKE_OIL_GPR_DIFF@199")

    # click some parameters
    select_parameter(dash_duo, plugin, "BPR_138_PERSISTENCE")
    select_parameter(dash_duo, plugin, "OP1_DIVERGENCE_SCALE")

    # clear ensemble selection
    clear_all = dash_duo.find_element(
        "#" + plugin.uuid("selected-ensemble-dropdown") + " span.Select-clear-zone"
    )
    clear_all.click()

    # wait a bit for the page to update
    wait_a_bit(dash_duo)

    # verify all plots are gone
    plots = dash_duo.find_elements(".dash-graph")
    assert len(plots) == 0

    # verify no responses are selected
    chosen_responses = dash_duo.find_elements(
        "#" + plugin.uuid("parameter-deactivator-resp") + " .Select-value"
    )
    assert len(chosen_responses) == 0

    # verify no parameters are selected
    chosen_parameters = dash_duo.find_elements(
        "#" + plugin.uuid("parameter-deactivator-param") + " .Select-value"
    )
    assert len(chosen_parameters) == 0

    # assert dash_duo.get_logs() == [], "browser console should contain no error"


@pytest.mark.browser_test
def test_axis_labels(mock_data, dash_duo):
    """test_axis_labels loads two different plots in the plot view and checks
    that axes are labelled correctly"""

    plugin = setup_plugin(
        dash_duo, __name__, ResponseComparison, window_size=(1024, 2048)
    )

    # find the right ensemble which has mock data prepared for this test
    wanted_ensemble_name = "default3"
    select_ensemble(dash_duo, plugin, wanted_ensemble_name)

    # click two responses, with specified names
    wanted_responses = ["FGPT", "FOPR"]

    for response in wanted_responses:
        select_response(dash_duo, plugin, response)

    # check that both have Value as y axis label
    for response in wanted_responses:
        y_axis_title_selector = f"#{plugin.uuid(response)} text.ytitle"
        dash_duo.wait_for_text_to_equal(y_axis_title_selector, "Value")

    # check that one has date, the other has index as x axis label
    date_plot_id = plugin.uuid("FOPR")
    dash_duo.wait_for_text_to_equal(f"#{date_plot_id} text.xtitle", "Date")

    index_plot_id = plugin.uuid("FGPT")
    dash_duo.wait_for_text_to_equal(f"#{index_plot_id} text.xtitle", "Index")

    # assert dash_duo.get_logs() == [], "browser console should contain no error"
