import dash
from webviz_ert.plugins._response_comparison import ResponseComparison
from tests.conftest import select_first
from selenium.common.exceptions import TimeoutException


def test_plot_view(
    mock_data,
    dash_duo,
):
    # This test selects an ensemble from the ensemble-multi-selector
    # then selects a response and parameter and checks that the
    # DOM element for both are created.
    app = dash.Dash(__name__)

    plugin = ResponseComparison(app, project_identifier=None)
    layout = plugin.layout
    app.layout = layout
    dash_duo.start_server(app)
    windowsize = (630, 1200)
    dash_duo.driver.set_window_size(*windowsize)

    ensemble_name = select_first(dash_duo, "#" + plugin.uuid("ensemble-multi-selector"))

    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("selected-ensemble-dropdown"),
        ensemble_name,
        timeout=4,
    )

    resp_select = dash_duo.find_element(
        "#" + plugin.uuid("parameter-selector-multi-resp")
    )

    x, y = (0.5, 0.1)
    dash_duo.click_at_coord_fractions(resp_select, x, y)
    dash_duo.wait_for_element("#" + plugin.uuid("SNAKE_OIL_GPR_DIFF"))

    param_select = dash_duo.find_element(
        "#" + plugin.uuid("parameter-selector-multi-param")
    )
    param_select.click()

    x, y = (0.5, 0.1)
    # double click's for the sake if other parameter comes first
    dash_duo.click_at_coord_fractions(param_select, x, y)
    param_select.click()
    dash_duo.click_at_coord_fractions(param_select, x, y)
    dash_duo.wait_for_element("#" + plugin.uuid("BPR_138_PERSISTENCE"))

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

    app = dash.Dash(__name__)

    plugin = ResponseComparison(app, project_identifier=None)
    layout = plugin.layout
    app.layout = layout
    dash_duo.start_server(app)
    windowsize = (1024, 3600)
    dash_duo.driver.set_window_size(*windowsize)

    ensemble_name = select_first(dash_duo, "#" + plugin.uuid("ensemble-multi-selector"))

    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("selected-ensemble-dropdown"),
        ensemble_name,
        timeout=4,
    )

    resp_select = dash_duo.find_element(
        "#" + plugin.uuid("parameter-selector-multi-resp")
    )

    # click the response, and check that the response graph appears
    responseName = "SNAKE_OIL_GPR_DIFF"

    x, y = (0.5, 0.1)
    dash_duo.click_at_coord_fractions(resp_select, x, y)
    dash_duo.wait_for_element("#" + plugin.uuid(responseName))

    param_select = dash_duo.find_element(
        "#" + plugin.uuid("parameter-selector-multi-param")
    )
    param_select.click()

    # triple click to select two first parameters (not sure why triple is
    # necessary), and check that the two parameter plots appear
    dash_duo.click_at_coord_fractions(param_select, x, y)
    dash_duo.wait_for_element("#" + plugin.uuid("BPR_138_PERSISTENCE"))
    param_select.click()
    dash_duo.click_at_coord_fractions(param_select, x, y)
    param_select.click()
    dash_duo.click_at_coord_fractions(param_select, x, y)
    dash_duo.wait_for_element("#" + plugin.uuid("OP1_DIVERGENCE_SCALE"))

    # clear parameter selection
    clear_all = dash_duo.find_element(
        "#" + plugin.uuid("parameter-deactivator-param") + " span.Select-clear-zone"
    )
    dash_duo.click_at_coord_fractions(clear_all, 0.5, 0.5)

    # wait a bit for the page to update
    try:
        dash_duo.wait_for_element(".foo-baarrrrr", timeout=0.1)
    except TimeoutException:
        pass

    # verify only expected response plot is left in place
    plots = dash_duo.find_elements(".dash-graph")
    assert responseName in plots[0].get_attribute("id")
    assert len(plots) == 1

    assert dash_duo.get_logs() == [], "browser console should contain no error"
