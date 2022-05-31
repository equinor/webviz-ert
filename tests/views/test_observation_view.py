import dash
from webviz_ert.plugins._observation_analyzer import ObservationAnalyzer
from tests.conftest import select_first, get_options, select_by_name


def test_observation_analyzer_view_ensemble_no_observations(
    mock_data,
    dash_duo,
):
    # This test selects an ensemble from the ensemble-multi-selector
    # then selects a response and parameter and checks that the
    # DOM element for both are created.
    app = dash.Dash(__name__)

    plugin = ObservationAnalyzer(app, project_identifier=None)
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

    resp_opt = get_options(dash_duo, "#" + plugin.uuid("response-selector"))
    assert resp_opt == ["Select..."]

    assert dash_duo.get_logs() == [], "browser console should contain no error"


def test_observation_analyzer_view_ensemble_with_observations(
    mock_data,
    dash_duo,
):
    # This test selects an ensemble from the ensemble-multi-selector
    # then selects a response and parameter and checks that the
    # DOM element for both are created.
    app = dash.Dash(__name__)

    plugin = ObservationAnalyzer(app, project_identifier=None)
    layout = plugin.layout
    app.layout = layout
    dash_duo.start_server(app)
    windowsize = (630, 1200)
    dash_duo.driver.set_window_size(*windowsize)

    ensemble_name = select_by_name(
        dash_duo=dash_duo,
        selector="#" + plugin.uuid("ensemble-multi-selector"),
        name="default3",
    )

    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("selected-ensemble-dropdown"),
        ensemble_name,
        timeout=4,
    )

    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("response-selector"),
        "FOPR",
        timeout=4,
    )

    assert dash_duo.get_logs() == [], "browser console should contain no error"
