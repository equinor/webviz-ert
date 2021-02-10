import dash
import ertviz
from ertviz.plugins._parameter_comparison import ParameterComparison


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

    ensemble_elements = dash_duo.find_element(".ert-ensemble-selector-large")
    dash_duo.wait_for_element("#" + plugin.uuid("parameter-selector-multi-params"))

    x, y = (0.5, 0.15)
    dash_duo.click_at_coord_fractions(ensemble_elements, x, y)

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
