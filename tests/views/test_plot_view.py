import dash
from webviz_ert.plugins._response_comparison import ResponseComparison
from tests.conftest import (
    setup_plugin,
    select_ensemble,
    select_parameter,
    select_response,
    wait_a_bit,
)


def test_plot_view(
    mock_data,
    dash_duo,
):
    # This test selects an ensemble from the ensemble-multi-selector
    # then selects a response and parameter and checks that the
    # DOM element for both are created.
    plugin = setup_plugin(dash_duo, __name__, ResponseComparison)

    select_ensemble(dash_duo, plugin)

    select_response(dash_duo, plugin, "SNAKE_OIL_GPR_DIFF")

    select_parameter(dash_duo, plugin, "BPR_138_PERSISTENCE")

    assert dash_duo.get_logs() == [], "browser console should contain no error"


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

    response_name = "SNAKE_OIL_GPR_DIFF"

    # click the response, and check that the response graph appears
    select_response(dash_duo, plugin, response_name)

    # click some parameters
    select_parameter(dash_duo, plugin, "BPR_138_PERSISTENCE")
    select_parameter(dash_duo, plugin, "OP1_DIVERGENCE_SCALE")

    # clear parameter selection
    clear_all = dash_duo.find_element(
        "#" + plugin.uuid("parameter-deactivator-param") + " span.Select-clear-zone"
    )
    dash_duo.click_at_coord_fractions(clear_all, 0.5, 0.5)

    # wait a bit for the page to update
    wait_a_bit(dash_duo)

    # verify only expected response plot is left in place
    plots = dash_duo.find_elements(".dash-graph")
    assert response_name in plots[0].get_attribute("id")
    assert len(plots) == 1

    assert dash_duo.get_logs() == [], "browser console should contain no error"


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
    select_response(dash_duo, plugin, "SNAKE_OIL_GPR_DIFF")

    # click some parameters
    select_parameter(dash_duo, plugin, "BPR_138_PERSISTENCE")
    select_parameter(dash_duo, plugin, "OP1_DIVERGENCE_SCALE")

    # clear ensemble selection
    clear_all = dash_duo.find_element(
        "#" + plugin.uuid("selected-ensemble-dropdown") + " span.Select-clear-zone"
    )
    dash_duo.click_at_coord_fractions(clear_all, 0.5, 0.5)

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

    assert dash_duo.get_logs() == [], "browser console should contain no error"
