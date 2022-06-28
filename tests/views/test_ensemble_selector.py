import dash
from webviz_ert.assets import get_color
from webviz_ert.plugins import ParameterComparison
from tests.conftest import select_first, get_options
from tests.data.snake_oil_data import all_ensemble_names
from tests.conftest import setup_plugin, select_ensemble


def test_ensemble_refresh(
    mock_data,
    dash_duo,
):
    plugin = setup_plugin(dash_duo, __name__, ParameterComparison)

    ensemble_selector_id = plugin.uuid("ensemble-multi-selector")
    initial_cases = get_options(dash_duo, "#" + ensemble_selector_id)

    # Select first ensemble
    first_ensemble_name = select_ensemble(dash_duo, plugin)

    # Select a parameter
    param_name = select_first(
        dash_duo, "#" + plugin.uuid("parameter-selector-multi-param")
    )

    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("parameter-deactivator-param"), f"×{param_name}", timeout=4
    )

    selected_params = get_options(
        dash_duo, "#" + plugin.uuid("parameter-deactivator-param")
    )

    # Select second ensemble
    second_ensemble_name = select_ensemble(dash_duo, plugin)

    selected_params_2 = get_options(
        dash_duo, "#" + plugin.uuid("parameter-deactivator-param")
    )

    # Check selected parameters are not duplicated
    assert len(selected_params) == len(set(selected_params_2)), "Duplicat parameter"

    # Check only expected selectable options are available
    expected_cases_after_selection = list(
        filter(
            lambda ens: ens not in (first_ensemble_name, second_ensemble_name),
            all_ensemble_names,
        )
    )
    cases_after_selection = get_options(dash_duo, "#" + ensemble_selector_id)
    assert sorted(cases_after_selection) == sorted(expected_cases_after_selection)

    # Click the refresh button
    ensemble_refresh = dash_duo.find_element(
        "#" + plugin.uuid("ensemble-refresh-button")
    )
    ensemble_refresh.click()

    # Check clicking refresh button also removes the selected parameters and options
    dash_duo.wait_for_text_to_equal(
        "#" + plugin.uuid("parameter-selector-multi-param"),
        "",
        timeout=4,
    )

    dash_duo.wait_for_text_to_equal(
        "#" + plugin.uuid("parameter-deactivator-param"),
        "",
        timeout=4,
    )

    # Check after the refresh all the initial ensemble cases are available as
    # options
    refreshed_cases = get_options(dash_duo, "#" + ensemble_selector_id)
    assert refreshed_cases == initial_cases


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
