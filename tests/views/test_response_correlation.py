import dash
from webviz_ert.plugins._response_correlation import ResponseCorrelation
from webviz_ert.plugins._response_comparison import ResponseComparison
from tests.conftest import select_first, select_by_name


def test_response_correlation_view(
    mock_data,
    dash_duo,
):
    app = dash.Dash(__name__)

    plugin = ResponseCorrelation(app, project_identifier=None)
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

    dash_duo.select_dcc_dropdown("#" + plugin.uuid("element-dropdown-resp"), index=0)

    param_select = dash_duo.find_element(
        "#" + plugin.uuid("parameter-selector-multi-param")
    )
    param_select.click()

    x, y = (0.5, 0.1)
    # double click's for the sake if other parameter comes first
    dash_duo.click_at_coord_fractions(param_select, x, y)

    response_views = dash_duo.find_elements(".ert-view-cell")
    assert len(response_views) == 4

    assert dash_duo.get_logs() == [], "browser console should contain no error"


def test_response_selector_sorting(mock_data, dash_duo):

    app = dash.Dash(__name__)
    plugin = ResponseComparison(app, project_identifier=None)
    layout = plugin.layout
    app.layout = layout
    dash_duo.start_server(app)
    windowsize = (630, 1200)
    dash_duo.driver.set_window_size(*windowsize)

    ensemble_name = select_by_name(
        dash_duo=dash_duo,
        selector="#" + plugin.uuid("ensemble-multi-selector"),
        name="nr_42",
    )

    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("selected-ensemble-dropdown"),
        ensemble_name,
        timeout=4,
    )

    response_selector_container = dash_duo.find_element(
        "#" + plugin.uuid("container-parameter-selector-multi-resp")
    )
    response_list = response_selector_container.text.split("\n")

    assert response_list[0] == "test_response"
    assert response_list[1] == "test_response_4"
    assert response_list[2] == "test_response_44"
    assert response_list[3] == "test_response_99"
