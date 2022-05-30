import dash
from webviz_ert.assets import get_color
from webviz_ert.plugins import ParameterComparison
from tests.conftest import select_first, get_options


def test_ensemble_refresh(
    mock_data,
    dash_duo,
):
    app = dash.Dash(__name__)

    plugin = ParameterComparison(app, project_identifier=None)
    layout = plugin.layout
    app.layout = layout
    dash_duo.start_server(app)
    windowsize = (630, 1200)
    dash_duo.driver.set_window_size(*windowsize)

    expected_cases = get_options(dash_duo, "#" + plugin.uuid("ensemble-multi-selector"))

    # Select first ensemble
    ensemble_name = select_first(dash_duo, "#" + plugin.uuid("ensemble-multi-selector"))
    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("selected-ensemble-dropdown"),
        ensemble_name,
        timeout=4,
    )

    # Select a parameter
    param_name = select_first(
        dash_duo, "#" + plugin.uuid("parameter-selector-multi-params")
    )

    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("parameter-deactivator-params"), f"×{param_name}", timeout=4
    )

    selected_params = get_options(
        dash_duo, "#" + plugin.uuid("parameter-deactivator-params")
    )

    # Select second ensemble
    ensemble_name = select_first(dash_duo, "#" + plugin.uuid("ensemble-multi-selector"))
    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("selected-ensemble-dropdown"),
        ensemble_name,
        timeout=4,
    )

    selected_params_2 = get_options(
        dash_duo, "#" + plugin.uuid("parameter-deactivator-params")
    )

    # Check selected parameters are not duplicated
    assert len(selected_params) == len(set(selected_params_2)), "Duplicat parameter"

    # Check only two more selectable options is available
    cases = get_options(dash_duo, "#" + plugin.uuid("ensemble-multi-selector"))
    assert cases == ["nr_42", "default3"]

    # Click the refresh button
    ensemble_refresh = dash_duo.find_element(
        "#" + plugin.uuid("ensemble-refresh-button")
    )
    ensemble_refresh.click()

    # Check clicking refresh button also removes the selected parameters and options
    dash_duo.wait_for_text_to_equal(
        "#" + plugin.uuid("parameter-selector-multi-params"),
        "",
        timeout=4,
    )

    dash_duo.wait_for_text_to_equal(
        "#" + plugin.uuid("parameter-deactivator-params"),
        "",
        timeout=4,
    )

    # Check after the refresh all the initial ensemble cases are available as options
    refreshed_cases = get_options(
        dash_duo, "#" + plugin.uuid("ensemble-multi-selector")
    )
    assert refreshed_cases == expected_cases


def test_ensemble_color(mock_data, dash_duo):
    app = dash.Dash(__name__)
    plugin = ParameterComparison(app, project_identifier=None)
    app.layout = plugin.layout
    dash_duo.start_server(app)

    windowsize = (630, 1200)
    dash_duo.driver.set_window_size(*windowsize)

    ensembles = get_options(dash_duo, "#" + plugin.uuid("ensemble-multi-selector"))

    for _ in ensembles:
        ensemble_name = select_first(
            dash_duo, "#" + plugin.uuid("ensemble-multi-selector")
        )
        dash_duo.wait_for_contains_text(
            "#" + plugin.uuid("selected-ensemble-dropdown"),
            ensemble_name,
            timeout=4,
        )

    selected_ensembles = dash_duo.find_elements(
        "#" + plugin.uuid("selected-ensemble-dropdown") + " div div.Select-value"
    )
    for idx, ensemble in enumerate(selected_ensembles):
        color = ensemble.value_of_css_property("background-color")
        expected_color = get_color(idx)
        assert color.replace(" ", "") == expected_color
