import dash
import webviz_ert
from webviz_ert.plugins._response_comparison import ResponseComparison
from tests.conftest import select_first


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
