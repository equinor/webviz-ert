import pytest

from selenium.webdriver.common.keys import Keys
from webviz_ert.plugins import ParameterComparison
from tests.conftest import setup_plugin, select_ensemble, select_by_name


@pytest.mark.browser_test
def test_parameter_selector(
    mock_data,
    dash_duo,
):
    plugin = setup_plugin(dash_duo, __name__, ParameterComparison)
    select_ensemble(dash_duo, plugin)

    dash_duo.wait_for_element("#" + plugin.uuid("parameter-selector-multi-param"))

    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("parameter-selector-multi-param"),
        "SNAKE_OIL_PARAM:BPR_138_PERSISTENCE",
    )

    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("parameter-selector-multi-param"),
        "SNAKE_OIL_PARAM:OP1_DIVERGENCE_SCALE",
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
        "#" + plugin.uuid("parameter-selector-filter-param"), "OP1"
    )
    dash_duo.wait_for_text_to_equal(
        "#" + plugin.uuid("parameter-selector-multi-param"),
        "SNAKE_OIL_PARAM:OP1_DIVERGENCE_SCALE",
    )

    parameter_selector_container = dash_duo.find_element(
        "#" + plugin.uuid("container-parameter-selector-multi-param")
    )

    assert parameter_selector_container.is_displayed()
    button_hide = dash_duo.find_element("#" + plugin.uuid("parameter-selector-button"))
    button_hide.click()
    parameter_selector_container = dash_duo.wait_for_element_by_css_selector(
        ".ert-parameter-selector-container-hide"
    )
    # assert dash_duo.get_logs() == []


@pytest.mark.browser_test
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
        "SNAKE_OIL_PARAM:BPR_138_PERSISTENCE",
    )
    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("parameter-selector-multi-param"),
        "OP1_DIVERGENCE_SCALE",
    )
    first_elem, _ = parameter_selector_container.text.split("\n")

    param_selector_id = plugin.uuid("parameter-selector-multi-param")
    select_by_name(
        dash_duo, f"#{param_selector_id}", "SNAKE_OIL_PARAM:BPR_138_PERSISTENCE"
    )

    parameter_deactivator = dash_duo.find_element(
        "#" + plugin.uuid("parameter-deactivator-param")
    )

    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("parameter-deactivator-param"),
        "×SNAKE_OIL_PARAM:BPR_138_PERSISTENCE",
    )
    parameter_deactivator.click()
    dash_duo.clear_input(parameter_deactivator)

    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("parameter-deactivator-param"), ""
    )

    parameter_selector_input = dash_duo.find_element(
        "#" + plugin.uuid("parameter-selector-filter-param")
    )
    parameter_selector_input.send_keys(Keys.ENTER)
    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("parameter-deactivator-param"), ""
    )

    parameter_selector_input.send_keys("SNAKE_OIL_PARAM:OP1")

    dash_duo.wait_for_text_to_equal(
        "#" + plugin.uuid("parameter-selector-filter-param"), "SNAKE_OIL_PARAM:OP1"
    )
    dash_duo.wait_for_text_to_equal(
        "#" + plugin.uuid("parameter-selector-multi-param"),
        "SNAKE_OIL_PARAM:OP1_DIVERGENCE_SCALE",
    )
    parameter_selector_input.send_keys(Keys.ENTER)

    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("parameter-deactivator-param"), ""
    )

    select_by_name(
        dash_duo, f"#{param_selector_id}", "SNAKE_OIL_PARAM:OP1_DIVERGENCE_SCALE"
    )
    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("parameter-deactivator-param"),
        "×SNAKE_OIL_PARAM:OP1_DIVERGENCE_SCALE",
    )

    # assert dash_duo.get_logs() == []


@pytest.mark.browser_test
def test_parameter_selector_sorting(
    mock_data,
    dash_duo,
):
    plugin = setup_plugin(dash_duo, __name__, ParameterComparison)

    wanted_ensemble_name = "nr_42"
    select_ensemble(dash_duo, plugin, wanted_ensemble_name)

    expected_parameters = [
        "SNAKE_OIL_PARAM:BPR_138_PERSISTENCE",
        "SNAKE_OIL_PARAM:OP1_DIVERGENCE_SCALE",
    ]

    parameter_selector_container_id = "#" + plugin.uuid(
        "container-parameter-selector-multi-param"
    )
    dash_duo.wait_for_text_to_equal(
        parameter_selector_container_id, "\n".join(expected_parameters)
    )
