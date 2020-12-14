from unittest import mock
from tests.conftest import mocked_requests_get, mocked_get_info, mocked_get_response_url
from ertviz.data_loader import get_ensemble_url
from ertviz.models import Response


@mock.patch("ertviz.data_loader.requests.get", side_effect=mocked_requests_get)
@mock.patch("ertviz.data_loader.get_info", side_effect=mocked_get_info)
@mock.patch(
    "ertviz.models.response.get_response_url", side_effect=mocked_get_response_url
)
def test_ensemble_model(mock_get, mock_get_info, mock_get_response_url):
    resp_model = Response(
        "SNAKE_OIL_GPR_DIFF",
        ensemble_id=1,
        response_id="SNAKE_OIL_GPR_DIFF",
    )
    assert resp_model.name == "SNAKE_OIL_GPR_DIFF"
    assert len(resp_model.realizations) == 1
