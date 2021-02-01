import dash
import ertviz
from unittest import mock
from ertviz.plugins._response_comparison import ResponseComparison
from tests.data.snake_oil_data import ensembles_response
from tests.conftest import (
    mocked_requests_get,
    mocked_read_csv,
    mocked_get_info,
    mocked_get_ensemble_url,
    mocked_get_parameter_data_url,
    mocked_get_response_url,
)


@mock.patch("ertviz.data_loader.requests.get", side_effect=mocked_requests_get)
@mock.patch("ertviz.data_loader.pandas.read_csv", side_effect=mocked_read_csv)
@mock.patch("ertviz.data_loader.get_info", side_effect=mocked_get_info)
@mock.patch(
    "ertviz.models.ensemble_model.get_ensemble_url", side_effect=mocked_get_ensemble_url
)
@mock.patch(
    "ertviz.models.parameter_model.get_parameter_data_url",
    side_effect=mocked_get_parameter_data_url,
)
@mock.patch(
    "ertviz.models.response.get_response_url", side_effect=mocked_get_response_url
)
def test_plot_view(
    mock_get,
    mock_get_csv,
    mock_get_info,
    mock_get_ensemble_url,
    mock_get_parameter_data_url,
    mock_get_response_url,
    dash_duo,
    monkeypatch,
    mocker,
):
    # This test selects an ensemble from the ensemble-selector
    # then selects a response and parameter and checks that the
    # DOM element for both are created.
    # The ensemble-selector has no API and the position for the
    # ensemble might change.
    app = dash.Dash(__name__)

    plugin = ResponseComparison(app, project_identifier=None)
    layout = plugin.layout
    app.layout = layout
    dash_duo.start_server(app)
    windowsize = (630, 1200)
    dash_duo.driver.set_window_size(*windowsize)
    ensemble_elements = dash_duo.find_element(".ert-ensemble-selector-large")
    dash_duo.wait_for_element("#" + plugin.uuid("response-selector"))

    # The position is hard coded coordinates normalized to the extent of the
    # ensemble-selector
    x, y = (0.5, 0.15)
    dash_duo.click_at_coord_fractions(ensemble_elements, x, y)
    resp_select_el = dash_duo.find_element("#" + plugin.uuid("response-selector"))

    dash_duo.select_dcc_dropdown(resp_select_el, index=0)
    dash_duo.wait_for_element("#" + plugin.uuid("SNAKE_OIL_GPR_DIFF"))

    param_select_el = dash_duo.find_element("#" + plugin.uuid("parameter-selector"))
    dash_duo.select_dcc_dropdown(param_select_el, index=0)
    dash_duo.wait_for_element("#" + plugin.uuid("BPR_138_PERSISTENCE"))

    assert dash_duo.get_logs() == [], "browser console should contain no error"
