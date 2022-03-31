import dash
import webviz_ert

from selenium.webdriver.common.keys import Keys
from webviz_ert.plugins import ParameterComparison
from tests.conftest import select_first


def test_parameter_selector(
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

    ensemble_name = select_first(dash_duo, "#" + plugin.uuid("ensemble-multi-selector"))
    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("selected-ensemble-dropdown"),
        ensemble_name,
        timeout=4,
    )

    dash_duo.wait_for_element("#" + plugin.uuid("parameter-selector-multi-params"))

    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("parameter-selector-multi-params"),
        "BPR_138_PERSISTENCE",
        timeout=4,
    )

    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("parameter-selector-multi-params"),
        "OP1_DIVERGENCE_SCALE",
        timeout=4,
    )

    paremeter_deactivator = dash_duo.find_element(
        "#" + plugin.uuid("parameter-deactivator-params")
    )

    paremeter_deactivator.click()

    parameter_selector_input = dash_duo.find_element(
        "#" + plugin.uuid("parameter-selector-filter-params")
    )

    parameter_selector_input.send_keys("OP1")

    dash_duo.wait_for_text_to_equal(
        "#" + plugin.uuid("parameter-selector-filter-params"), "OP1", timeout=4
    )
    dash_duo.wait_for_text_to_equal(
        "#" + plugin.uuid("parameter-selector-multi-params"),
        "OP1_DIVERGENCE_SCALE",
        timeout=4,
    )

    parameter_selector_container = dash_duo.find_element(
        "#" + plugin.uuid("container-parameter-selector-multi-params")
    )

    assert parameter_selector_container.is_displayed() is True
    button_hide = dash_duo.find_element(
        "#" + plugin.uuid("parameter-selector-button-params")
    )
    button_hide.click()
    parameter_selector_container = dash_duo.wait_for_element_by_css_selector(
        ".ert-parameter-selector-container-hide"
    )
    assert dash_duo.get_logs() == []


def test_search_input_return_functionality(
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

    ensemble_name = select_first(dash_duo, "#" + plugin.uuid("ensemble-multi-selector"))
    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("selected-ensemble-dropdown"),
        ensemble_name,
        timeout=4,
    )

    dash_duo.wait_for_element("#" + plugin.uuid("parameter-selector-multi-params"))

    parameter_selector_container = dash_duo.find_element(
        "#" + plugin.uuid("container-parameter-selector-multi-params")
    )

    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("parameter-selector-multi-params"),
        "BPR_138_PERSISTENCE",
        timeout=4,
    )
    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("parameter-selector-multi-params"),
        "OP1_DIVERGENCE_SCALE",
        timeout=4,
    )
    first_elem, _ = parameter_selector_container.text.split("\n")

    dash_duo.click_at_coord_fractions(parameter_selector_container, 0.1, 0.05)

    parameter_deactivator = dash_duo.find_element(
        "#" + plugin.uuid("parameter-deactivator-params")
    )

    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("parameter-deactivator-params"), f"×{first_elem}", timeout=4
    )
    parameter_deactivator.click()
    dash_duo.clear_input(parameter_deactivator)

    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("parameter-deactivator-params"), "", timeout=4
    )

    parameter_selector_input = dash_duo.find_element(
        "#" + plugin.uuid("parameter-selector-filter-params")
    )
    parameter_selector_input.send_keys(Keys.ENTER)
    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("parameter-deactivator-params"), "", timeout=4
    )

    parameter_selector_input.send_keys("OP1")

    dash_duo.wait_for_text_to_equal(
        "#" + plugin.uuid("parameter-selector-filter-params"), "OP1", timeout=4
    )
    dash_duo.wait_for_text_to_equal(
        "#" + plugin.uuid("parameter-selector-multi-params"),
        "OP1_DIVERGENCE_SCALE",
        timeout=4,
    )
    parameter_selector_input.send_keys(Keys.ENTER)

    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("parameter-deactivator-params"), "", timeout=4
    )
    dash_duo.click_at_coord_fractions(parameter_selector_container, 0.1, 0.05)
    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("parameter-deactivator-params"),
        "×OP1_DIVERGENCE_SCALE",
        timeout=4,
    )

    assert dash_duo.get_logs() == []


def test_parameter_selector_sorting(
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

    ensemble_selector = dash_duo.find_element(
        "#" + plugin.uuid("ensemble-multi-selector")
    )

    dash_duo.click_at_coord_fractions(ensemble_selector, 0.1, 0.25)
    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("selected-ensemble-dropdown"),
        "nr_42",
        timeout=4,
    )

    parameter_selector_container = dash_duo.find_element(
        "#" + plugin.uuid("container-parameter-selector-multi-params")
    )
    parameter_list = parameter_selector_container.text.split("\n")

    assert parameter_list[0] == "test_parameter_1"
    assert parameter_list[1] == "test_parameter_11"
    assert parameter_list[2] == "test_parameter_2::a"
    assert parameter_list[3] == "test_parameter_2::b"
    assert parameter_list[4] == "test_parameter_77"
