import dash
import ertviz
from ertviz.plugins._response_comparison import ResponseComparison


def test_plot_view(
    data_loader,
    dash_duo,
):
    # This test selects an ensemble from the ensemble-selector
    # then selects a response and parameter and checks that the
    # DOM element for both are created.
    # The ensemble-selector has no API and the position for the
    # ensemble might change.
    app = dash.Dash(__name__)

    plugin = ResponseComparison(app, project_identifier=None)
    layout = plugin.layout
    app.layout = layout
    dash_duo.start_server(app)
    windowsize = (630, 1200)
    dash_duo.driver.set_window_size(*windowsize)
    ensemble_elements = dash_duo.find_element(".ert-ensemble-selector-large")
    dash_duo.wait_for_element("#" + plugin.uuid("response-selector"))

    # The position is hard coded coordinates normalized to the extent of the
    # ensemble-selector
    x, y = (0.5, 0.15)
    dash_duo.click_at_coord_fractions(ensemble_elements, x, y)
    resp_select_el = dash_duo.find_element("#" + plugin.uuid("response-selector"))

    dash_duo.select_dcc_dropdown(resp_select_el, index=0)
    dash_duo.wait_for_element("#" + plugin.uuid("SNAKE_OIL_GPR_DIFF"))

    param_select_el = dash_duo.find_element("#" + plugin.uuid("parameter-selector"))
    dash_duo.select_dcc_dropdown(param_select_el, index=0)
    dash_duo.wait_for_element("#" + plugin.uuid("BPR_138_PERSISTENCE"))

    assert dash_duo.get_logs() == [], "browser console should contain no error"
