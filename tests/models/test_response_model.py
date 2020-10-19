from unittest import mock
from tests.conftest import mocked_requests_get
from ertviz.data_loader import get_ensemble_url
from ertviz.models import Response

@mock.patch("ertviz.data_loader.requests.get", side_effect=mocked_requests_get)
def test_ensemble_model(mock_get):
    resp_model = Response( "http://127.0.0.1:5000/ensembles/1/responses/SNAKE_OIL_GPR_DIFF")
    assert resp_model.name == "SNAKE_OIL_GPR_DIFF"
    assert len(resp_model.realizations) == 1
