from unittest import mock
from ertviz.models.ensemble_model import EnsembleModel
from ertviz.controllers.controller_functions import response_options
from tests.conftest import (
    mocked_requests_get,
    mocked_read_csv,
    mocked_get_info,
    mocked_get_ensemble_url,
    mocked_get_response_url,
)


@mock.patch("ertviz.data_loader.requests.get", side_effect=mocked_requests_get)
@mock.patch("ertviz.data_loader.pandas.read_csv", side_effect=mocked_read_csv)
@mock.patch("ertviz.data_loader.get_info", side_effect=mocked_get_info)
@mock.patch(
    "ertviz.models.ensemble_model.get_ensemble_url", side_effect=mocked_get_ensemble_url
)
@mock.patch(
    "ertviz.models.response.get_response_url", side_effect=mocked_get_response_url
)
def test_response_options(
    mock_get,
    mock_get_csv,
    mock_get_info,
    mocked_get_ensemble_url,
    mocked_get_response_url,
):
    ensemble3 = EnsembleModel(ensemble_id=3, project_id=None)
    ensemble4 = EnsembleModel(ensemble_id=4, project_id=None)

    options = response_options(response_filters=[], ensembles=[ensemble3, ensemble4])
    options_with_obs = response_options(
        response_filters=["obs"], ensembles=[ensemble3, ensemble4]
    )

    assert len(options) == 3
    assert len(options_with_obs) == 2
