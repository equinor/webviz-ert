import pytest
from webviz_ert.plugins import (
    ParameterComparison,
    ResponseComparison,
    ResponseCorrelation,
    ObservationAnalyzer,
)
from tests.conftest import (
    select_first,
    select_ensemble,
    select_parameter,
    select_response,
    setup_plugin,
    verify_key_in_dropdown,
)

parameter_keys = ["FIELD_PROPERTIES:POROSITY", "FIELD_PROPERTIES:X_MID_PERMEABILITY"]
response_keys = ["WGPT:PROD", "WWPT:PROD", "WOPT:PROD", "WWIT:INJ"]
response_keys_with_observations = ["WOPT:PROD"]


def _verify_keys_in_menu(dash_duo_handle, plugin, keys, selector):
    dash_duo_handle.wait_for_element("#" + plugin.uuid(selector))
    for key in keys:
        dash_duo_handle.wait_for_contains_text(
            "#" + plugin.uuid(selector),
            key,
        )


@pytest.mark.spe1
@pytest.mark.xfail(reason="Fails because ert>5 no longer supports ert-storage")
def test_webviz_parameter_comparison(dash_duo):
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
@pytest.mark.xfail(reason="Fails because ert>5 no longer supports ert-storage")
def test_webviz_response_correlation(dash_duo):
    plugin = setup_plugin(dash_duo, __name__, ResponseCorrelation)

    ensemble = "default"
    response = "WOPT:PROD"
    parameter = "FIELD_PROPERTIES:POROSITY::0"
    index = "2016-01-01"

    # Wait for the ensemble selector to be initialized
    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("ensemble-multi-selector"),
        ensemble,
    )
    select_ensemble(dash_duo, plugin, ensemble)

    _verify_keys_in_menu(
        dash_duo, plugin, parameter_keys, "parameter-selector-multi-param"
    )
    _verify_keys_in_menu(
        dash_duo,
        plugin,
        response_keys_with_observations,
        "parameter-selector-multi-resp",
    )

    select_response(dash_duo, plugin, response, wait_for_plot=False)
    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("parameter-deactivator-resp"),
        f"×{response}",
    )

    select_parameter(dash_duo, plugin, parameter, wait_for_plot=False)
    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("parameter-deactivator-param"),
        f"×{parameter}",
    )


@pytest.mark.spe1
@pytest.mark.xfail(reason="Fails because ert>5 no longer supports ert-storage")
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
@pytest.mark.xfail(reason="Fails because ert>5 no longer supports ert-storage")
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
