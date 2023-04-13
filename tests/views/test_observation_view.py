import pytest
from webviz_ert.plugins import ObservationAnalyzer
from tests.conftest import (
    get_options,
    select_ensemble,
    verify_key_in_dropdown,
    setup_plugin,
)


def test_observation_analyzer_view_ensemble_no_observations(
    mock_data,
    dash_duo,
):
    # This test selects an ensemble from the ensemble-multi-selector
    # where no response has any observations, and checks that no responses are
    # available in the response selector
    plugin = setup_plugin(dash_duo, __name__, ObservationAnalyzer)

    ensemble_name = select_ensemble(dash_duo, plugin)
    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("selected-ensemble-dropdown"),
        ensemble_name,
    )

    response_options_selector = f"#{plugin.uuid('response-selector')}"
    dash_duo.wait_for_text_to_equal(response_options_selector, "Select...")


def test_observation_analyzer_view_ensemble_with_observations(
    mock_data,
    dash_duo,
):
    # This test selects an ensemble from the ensemble-multi-selector that has
    # responses with observations, and checks that a response with observations
    # is present among the choosable responses.
    plugin = setup_plugin(dash_duo, __name__, ObservationAnalyzer)

    ensemble_name = select_ensemble(dash_duo, plugin, "default3")

    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("selected-ensemble-dropdown"),
        ensemble_name,
    )

    verify_key_in_dropdown(dash_duo, plugin.uuid("response-selector"), "FOPR")
