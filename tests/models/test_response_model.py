from unittest import mock
from tests.conftest import mocked_requests_get, mocked_get_info
from ertviz.data_loader import get_ensemble_url
from ertviz.models import Response


@mock.patch("ertviz.data_loader.requests.get", side_effect=mocked_requests_get)
@mock.patch("ertviz.data_loader.get_info", side_effect=mocked_get_info)
def test_ensemble_model(mock_get, mock_get_info):
    resp_model = Response(
        "SNAKE_OIL_GPR_DIFF",
        "http://127.0.0.1:5000/ensembles/1/responses/SNAKE_OIL_GPR_DIFF",
    )
    assert resp_model.name == "SNAKE_OIL_GPR_DIFF"
    assert len(resp_model.realizations) == 1
