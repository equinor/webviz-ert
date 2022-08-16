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

    ensemble_selector_id = f"#{plugin.uuid('ensemble-multi-selector')}"
    expected_initial_ensembles = [
        "default",
        "default_smoother_update",
        "default3",
        "nr_42",
    ]
    dash_duo.wait_for_text_to_equal(
        ensemble_selector_id, "\n".join(expected_initial_ensembles)
    )

    # Select first ensemble
    first_ensemble_name = select_ensemble(dash_duo, plugin)

    # Select a parameter
    first_parameter = select_first(
        dash_duo, "#" + plugin.uuid("parameter-selector-multi-param")
    )

    selected_parameters_finder = (
        f"#{plugin.uuid('parameter-deactivator-param')} " ".Select-value-label"
    )
    dash_duo.wait_for_contains_text(selected_parameters_finder, first_parameter)
    # for some reason, there is an empty label
    expected_selected_parameters = [first_parameter, " "]
    dash_duo.wait_for_text_to_equal(
        selected_parameters_finder, "\n".join(expected_selected_parameters)
    )

    # Select second ensemble
    second_ensemble_name = select_ensemble(dash_duo, plugin)

    # Check selected parameters are unchanged (in particular, not duplicated)
    dash_duo.wait_for_text_to_equal(
        selected_parameters_finder, "\n".join(expected_selected_parameters)
    )

    # Check only expected selectable options are available
    expected_ensembles_after_selection = list(
        filter(
            lambda ens: ens not in (first_ensemble_name, second_ensemble_name),
            all_ensemble_names,
        )
    )
    dash_duo.wait_for_text_to_equal(
        ensemble_selector_id, "\n".join(sorted(expected_ensembles_after_selection))
    )

    # Click the refresh button
    ensemble_refresh = dash_duo.find_element(
        "#" + plugin.uuid("ensemble-refresh-button")
    )
    ensemble_refresh.click()

    # Check clicking refresh button also removes the selected parameters and options
    dash_duo.wait_for_text_to_equal(
        "#" + plugin.uuid("parameter-selector-multi-param"),
        "",
    )

    dash_duo.wait_for_text_to_equal(
        "#" + plugin.uuid("parameter-deactivator-param"),
        "",
    )

    # Check after the refresh all the initial ensemble cases are available as
    # options
    dash_duo.wait_for_text_to_equal(
        ensemble_selector_id, "\n".join(expected_initial_ensembles)
    )


def test_ensemble_color(mock_data, dash_duo):
    plugin = setup_plugin(dash_duo, __name__, ParameterComparison, (630, 1200))

    ensembles = get_options(dash_duo, "#" + plugin.uuid("ensemble-multi-selector"))

    for _ in ensembles:
        ensemble_name = select_first(
            dash_duo, "#" + plugin.uuid("ensemble-multi-selector")
        )
        dash_duo.wait_for_contains_text(
            "#" + plugin.uuid("selected-ensemble-dropdown"),
            ensemble_name,
        )

    selected_ensembles = dash_duo.find_elements(
        "#" + plugin.uuid("selected-ensemble-dropdown") + " .Select-value"
    )
    for idx, ensemble in enumerate(selected_ensembles):
        color = ensemble.value_of_css_property("background-color")
        expected_color = get_color(idx)
        assert color.replace(" ", "") == expected_color
