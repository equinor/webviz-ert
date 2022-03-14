import dash
import pytest
from webviz_ert.plugins import (
    ParameterComparison,
    ResponseComparison,
    ResponseCorrelation,
    ObservationAnalyzer,
)
from tests.conftest import select_first

parameter_keys = ["FIELD_PROPERTIES:POROSITY", "FIELD_PROPERTIES:X_MID_PERMEABILITY"]
response_keys = ["WGPT:PROD", "WWPT:PROD", "WOPT:PROD", "WWIT:INJ"]


def _gen_plugin(dash_duo_handle, PluginClass):
    app = dash.Dash(__name__)
    plugin = PluginClass(app, project_identifier=None)
    layout = plugin.layout
    app.layout = layout
    dash_duo_handle.start_server(app)
    windowsize = (630, 2000)
    dash_duo_handle.driver.set_window_size(*windowsize)
    return plugin


def _verify_keys_in_menu(dash_duo_handle, plugin, keys, selector):
    dash_duo_handle.wait_for_element("#" + plugin.uuid(selector))
    for key in keys:
        dash_duo_handle.wait_for_contains_text(
            "#" + plugin.uuid(selector),
            key,
            timeout=10,
        )


@pytest.mark.spe1
def test_webviz_parameter_comparison(get_ensemble_id, dash_duo):
    # here we need the poke storage first - to get this test running
    _ = get_ensemble_id
    plugin = _gen_plugin(dash_duo, ParameterComparison)

    # Wait for the ensemble selector to be initialized
    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("ensemble-multi-selector"),
        "default",
        timeout=4,
    )

    ensemble_name = select_first(dash_duo, "#" + plugin.uuid("ensemble-multi-selector"))
    _verify_keys_in_menu(
        dash_duo, plugin, parameter_keys, "parameter-selector-multi-params"
    )


@pytest.mark.spe1
def test_webviz_response_correlation(dash_duo):
    plugin = _gen_plugin(dash_duo, ResponseCorrelation)

    # Wait for the ensemble selector to be initialized
    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("ensemble-multi-selector"),
        "default",
        timeout=4,
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
        "#" + plugin.uuid("response-info-text"),
        f"{response_name} @ 2015-02-01T00:00:00,\nparameter: {param_name}",
        30,
    )


@pytest.mark.spe1
def test_webviz_response_comparison(dash_duo):
    plugin = _gen_plugin(dash_duo, ResponseComparison)

    # Wait for the ensemble selector to be initialized
    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("ensemble-multi-selector"),
        "default",
        timeout=4,
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

    assert dash_duo.get_logs() == [], "browser console should contain no error"


@pytest.mark.spe1
def test_webviz_observation_analyzer(dash_duo):
    plugin = _gen_plugin(dash_duo, ObservationAnalyzer)

    # Wait for the ensemble selector to be initialized
    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("ensemble-multi-selector"),
        "default",
        timeout=4,
    )

    ensemble_name = select_first(dash_duo, "#" + plugin.uuid("ensemble-multi-selector"))
    _verify_keys_in_menu(dash_duo, plugin, ["WOPT:PROD"], "response-selector")
