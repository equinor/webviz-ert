from unittest import mock

from ertviz.ert_client import get_response

from tests.conftest import mocked_requests_get


@mock.patch("ertviz.data_loader.requests.get", side_effect=mocked_requests_get)
def test_get_response(mock_get):
    response_url = "http://127.0.0.1:5000/ensembles/1/responses/FOPR"
    response_0 = get_response("FOPR", response_url)

    assert response_0 is not None
    assert response_0.axis == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert len(response_0.realizations) == 1
    assert response_0.realizations[0].name == 0
    assert len(response_0.observations) == 1
    assert response_0.observations[0].name == "FOPR"


@mock.patch("ertviz.data_loader.requests.get", side_effect=mocked_requests_get)
def test_get_response_without_observations(mock_get):
    response_url = "http://127.0.0.1:5000/ensembles/1/responses/SNAKE_OIL_GPR_DIFF"
    response_0 = get_response("SNAKE_OIL_GPR_DIFF", response_url)

    assert response_0 is not None
    assert response_0.axis == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert len(response_0.realizations) == 1
    assert response_0.realizations[0].name == 0
    assert len(response_0.observations) == 0
