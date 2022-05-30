import dash
import webviz_ert

from selenium.webdriver.common.keys import Keys
from webviz_ert.plugins import ParameterComparison
from tests.conftest import setup_plugin, select_ensemble, select_by_name


def test_parameter_selector(
    mock_data,
    dash_duo,
):
    plugin = setup_plugin(dash_duo, __name__, ParameterComparison)
    select_ensemble(dash_duo, plugin)

    dash_duo.wait_for_element("#" + plugin.uuid("parameter-selector-multi-param"))

    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("parameter-selector-multi-param"),
        "BPR_138_PERSISTENCE",
        timeout=4,
    )

    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("parameter-selector-multi-param"),
        "OP1_DIVERGENCE_SCALE",
        timeout=4,
    )

    paremeter_deactivator = dash_duo.find_element(
        "#" + plugin.uuid("parameter-deactivator-param")
    )

    paremeter_deactivator.click()

    parameter_selector_input = dash_duo.find_element(
        "#" + plugin.uuid("parameter-selector-filter-param")
    )

    parameter_selector_input.send_keys("OP1")

    dash_duo.wait_for_text_to_equal(
        "#" + plugin.uuid("parameter-selector-filter-param"), "OP1", timeout=4
    )
    dash_duo.wait_for_text_to_equal(
        "#" + plugin.uuid("parameter-selector-multi-param"),
        "OP1_DIVERGENCE_SCALE",
        timeout=4,
    )

    parameter_selector_container = dash_duo.find_element(
        "#" + plugin.uuid("container-parameter-selector-multi-param")
    )

    assert parameter_selector_container.is_displayed() is True
    button_hide = dash_duo.find_element("#" + plugin.uuid("parameter-selector-button"))
    button_hide.click()
    parameter_selector_container = dash_duo.wait_for_element_by_css_selector(
        ".ert-parameter-selector-container-hide"
    )
    # assert dash_duo.get_logs() == []


def test_search_input_return_functionality(
    mock_data,
    dash_duo,
):
    plugin = setup_plugin(dash_duo, __name__, ParameterComparison)
    select_ensemble(dash_duo, plugin)

    parameter_selector_container = dash_duo.find_element(
        "#" + plugin.uuid("container-parameter-selector-multi-param")
    )

    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("parameter-selector-multi-param"),
        "BPR_138_PERSISTENCE",
        timeout=4,
    )
    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("parameter-selector-multi-param"),
        "OP1_DIVERGENCE_SCALE",
        timeout=4,
    )
    first_elem, _ = parameter_selector_container.text.split("\n")

    param_selector_id = plugin.uuid("parameter-selector-multi-param")
    select_by_name(dash_duo, f"#{param_selector_id}", "BPR_138_PERSISTENCE")

    parameter_deactivator = dash_duo.find_element(
        "#" + plugin.uuid("parameter-deactivator-param")
    )

    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("parameter-deactivator-param"),
        "×BPR_138_PERSISTENCE",
        timeout=4,
    )
    parameter_deactivator.click()
    dash_duo.clear_input(parameter_deactivator)

    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("parameter-deactivator-param"), "", timeout=4
    )

    parameter_selector_input = dash_duo.find_element(
        "#" + plugin.uuid("parameter-selector-filter-param")
    )
    parameter_selector_input.send_keys(Keys.ENTER)
    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("parameter-deactivator-param"), "", timeout=4
    )

    parameter_selector_input.send_keys("OP1")

    dash_duo.wait_for_text_to_equal(
        "#" + plugin.uuid("parameter-selector-filter-param"), "OP1", timeout=4
    )
    dash_duo.wait_for_text_to_equal(
        "#" + plugin.uuid("parameter-selector-multi-param"),
        "OP1_DIVERGENCE_SCALE",
        timeout=4,
    )
    parameter_selector_input.send_keys(Keys.ENTER)

    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("parameter-deactivator-param"), "", timeout=4
    )

    select_by_name(dash_duo, f"#{param_selector_id}", "OP1_DIVERGENCE_SCALE")
    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("parameter-deactivator-param"),
        "×OP1_DIVERGENCE_SCALE",
        timeout=4,
    )

    # assert dash_duo.get_logs() == []


def test_parameter_selector_sorting(
    mock_data,
    dash_duo,
):
    plugin = setup_plugin(dash_duo, __name__, ParameterComparison)

    wanted_ensemble_name = "nr_42"
    select_ensemble(dash_duo, plugin, wanted_ensemble_name)

    parameter_selector_container = dash_duo.find_element(
        "#" + plugin.uuid("container-parameter-selector-multi-param")
    )
    parameter_list = parameter_selector_container.text.split("\n")

    assert parameter_list[0] == "test_parameter_1"
    assert parameter_list[1] == "test_parameter_11"
    assert parameter_list[2] == "test_parameter_2::a"
    assert parameter_list[3] == "test_parameter_2::b"
    assert parameter_list[4] == "test_parameter_77"
