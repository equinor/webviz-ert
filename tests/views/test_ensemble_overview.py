import dash
import ertviz
from unittest import mock
from ertviz.plugins._ensemble_overview import EnsembleOverview
from tests.data.snake_oil_data import ensembles_response
from tests.conftest import (
    mocked_requests_get,
    mocked_read_csv,
    mocked_get_info,
    mocked_get_ensemble_url,
)


@mock.patch("ertviz.data_loader.requests.get", side_effect=mocked_requests_get)
@mock.patch("ertviz.data_loader.pandas.read_csv", side_effect=mocked_read_csv)
@mock.patch("ertviz.data_loader.get_info", side_effect=mocked_get_info)
@mock.patch(
    "ertviz.models.ensemble_model.get_ensemble_url", side_effect=mocked_get_ensemble_url
)
def test_ensemble_overview(
    mock_get,
    mock_get_csv,
    mock_get_info,
    mock_get_ensemble_url,
    dash_duo,
    monkeypatch,
    mocker,
):
    app = dash.Dash(__name__)

    plugin = EnsembleOverview(app, project_identifier=None)
    layout = plugin.layout
    app.layout = layout
    dash_duo.start_server(app)

    ensemble_elements = dash_duo.find_element(".ert-ensemble-selector-large")

    assert ensemble_elements.tag_name == "div"

    minimize_button = dash_duo.wait_for_element_by_css_selector(
        ".ert-ensemble-selector-view-toggle"
    )
    minimize_button.click()
    ensemble_elements = dash_duo.wait_for_element_by_css_selector(
        ".ert-ensemble-selector-small"
    )
    assert dash_duo.get_logs() == [], "browser console should contain no error"
