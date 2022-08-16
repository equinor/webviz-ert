import pytest
import dash
from tests.conftest import setup_plugin
from webviz_ert.plugins import (
    ResponseComparison,
    ObservationAnalyzer,
    ParameterComparison,
    ResponseCorrelation,
)


@pytest.mark.parametrize(
    "plugin_class,input",
    [
        pytest.param(ResponseComparison, True),
        pytest.param(ResponseComparison, False),
        pytest.param(ObservationAnalyzer, True),
        pytest.param(ObservationAnalyzer, False),
        pytest.param(ParameterComparison, True),
        pytest.param(ParameterComparison, False),
        pytest.param(ResponseCorrelation, True),
        pytest.param(ResponseCorrelation, False),
    ],
)
def test_displaying_beta_warning(plugin_class, input: bool, dash_duo):
    plugin = setup_plugin(dash_duo, __name__, plugin_class, beta=input)
    beta_warning_element = dash_duo.find_element("#" + plugin.uuid("beta-warning"))
    assert beta_warning_element.is_displayed() == input


skip_responses = "resp"
skip_parameters = "param"


@pytest.mark.parametrize(
    "plugin_class,skip",
    [
        pytest.param(ResponseComparison, [], id="ResponseComparison"),
        pytest.param(
            ObservationAnalyzer,
            [skip_responses, skip_parameters],
            id="ObservationAnalyzer",
        ),
        pytest.param(ParameterComparison, [skip_responses], id="ParameterComparison"),
        pytest.param(ResponseCorrelation, [], id="ResponseCorrelation"),
    ],
)
def test_selectors_visibility_toggle_button(plugin_class, skip, mock_data, dash_duo):
    # we test whether the selector visibility toggle button changes class on
    # all selectors, as expected

    plugin = setup_plugin(dash_duo, __name__, plugin_class, (2048, 1536))

    visibility_toggler = dash_duo.find_element(
        "#" + plugin.uuid("parameter-selector-button")
    )
    visibility_toggler.click()

    ensemble_container_class_prefix = "ert-ensemble-selector-container"
    dash_duo.wait_for_class_to_equal(
        f'#{plugin.uuid("container-ensemble-selector-multi")}',
        f"{ensemble_container_class_prefix}-hide",
    )

    variable_container_class_prefix = "ert-parameter-selector-container"
    if skip_responses not in skip:
        dash_duo.wait_for_class_to_equal(
            f'#{plugin.uuid("container-parameter-selector-multi-resp")}',
            f"{variable_container_class_prefix}-hide",
        )

    if skip_parameters not in skip:
        dash_duo.wait_for_class_to_equal(
            f'#{plugin.uuid("container-parameter-selector-multi-param")}',
            f"{variable_container_class_prefix}-hide",
        )

    # assert dash_duo.get_logs() == [], "browser console should contain no error"
