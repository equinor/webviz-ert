import dash
import pytest
from webviz_ert.plugins import (
    ParameterComparison,
    ResponseComparison,
    ResponseCorrelation,
    ObservationAnalyzer,
)
from tests.conftest import select_first, setup_plugin, verify_key_in_dropdown

parameter_keys = ["FIELD_PROPERTIES:POROSITY", "FIELD_PROPERTIES:X_MID_PERMEABILITY"]
response_keys = ["WGPT:PROD", "WWPT:PROD", "WOPT:PROD", "WWIT:INJ"]


def _verify_keys_in_menu(dash_duo_handle, plugin, keys, selector):
    dash_duo_handle.wait_for_element("#" + plugin.uuid(selector))
    for key in keys:
        dash_duo_handle.wait_for_contains_text(
            "#" + plugin.uuid(selector),
            key,
        )


@pytest.mark.spe1
def test_webviz_parameter_comparison(get_ensemble_id, dash_duo):
    # here we need the poke storage first - to get this test running
    _ = get_ensemble_id
    plugin = setup_plugin(dash_duo, __name__, ParameterComparison)

    # Wait for the ensemble selector to be initialized
    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("ensemble-multi-selector"),
        "default",
    )

    ensemble_name = select_first(dash_duo, "#" + plugin.uuid("ensemble-multi-selector"))
    _verify_keys_in_menu(
        dash_duo, plugin, parameter_keys, "parameter-selector-multi-param"
    )


@pytest.mark.spe1
def test_webviz_response_correlation(dash_duo):
    plugin = setup_plugin(dash_duo, __name__, ResponseCorrelation)

    # Wait for the ensemble selector to be initialized
    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("ensemble-multi-selector"),
        "default",
    )

    ensemble_name = select_first(dash_duo, "#" + plugin.uuid("ensemble-multi-selector"))
    _verify_keys_in_menu(
        dash_duo, plugin, parameter_keys, "parameter-selector-multi-param"
    )

    _verify_keys_in_menu(
        dash_duo, plugin, response_keys, "parameter-selector-multi-resp"
    )
    response_name = select_first(
        dash_duo, "#" + plugin.uuid("parameter-selector-multi-resp")
    )
    param_name = select_first(
        dash_duo, "#" + plugin.uuid("parameter-selector-multi-param")
    )
    dash_duo.wait_for_text_to_equal(
        "#" + plugin.uuid("info-text"),
        "".join(
            [
                f"RESPONSE: {response_name}",
                f"INDEX: 2015-02-01",
                f"PARAMETER: {param_name}",
            ]
        ),
    )


@pytest.mark.spe1
def test_webviz_response_comparison(dash_duo):
    plugin = setup_plugin(dash_duo, __name__, ResponseComparison)

    # Wait for the ensemble selector to be initialized
    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("ensemble-multi-selector"),
        "default",
    )

    ensemble_name = select_first(dash_duo, "#" + plugin.uuid("ensemble-multi-selector"))
    _verify_keys_in_menu(
        dash_duo, plugin, parameter_keys, "parameter-selector-multi-param"
    )

    _verify_keys_in_menu(
        dash_duo, plugin, response_keys, "parameter-selector-multi-resp"
    )

    response_name = select_first(
        dash_duo, "#" + plugin.uuid("parameter-selector-multi-resp")
    )
    #':' must be escaped in element ids
    resp_plot_id = "#" + plugin.uuid(response_name.replace(":", "\\:"))
    dash_duo.wait_for_element(resp_plot_id)

    param_name = select_first(
        dash_duo, "#" + plugin.uuid("parameter-selector-multi-param")
    )
    param_plot_id = "#" + plugin.uuid(param_name.replace(":", "\\:"))
    dash_duo.wait_for_element(param_plot_id)

    # assert dash_duo.get_logs() == [], "browser console should contain no error"


@pytest.mark.spe1
def test_webviz_observation_analyzer(dash_duo):
    plugin = setup_plugin(dash_duo, __name__, ObservationAnalyzer)

    # Wait for the ensemble selector to be initialized
    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("ensemble-multi-selector"),
        "default",
    )

    ensemble_name = select_first(dash_duo, "#" + plugin.uuid("ensemble-multi-selector"))
    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("selected-ensemble-dropdown"),
        ensemble_name,
    )

    verify_key_in_dropdown(dash_duo, plugin.uuid("response-selector"), "WOPT:PROD")
