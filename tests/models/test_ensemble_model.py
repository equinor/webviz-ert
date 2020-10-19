from unittest import mock
from tests.conftest import mocked_requests_get
from ertviz.data_loader import get_ensemble_url
from ertviz.models import EnsembleModel

@mock.patch("ertviz.data_loader.requests.get", side_effect=mocked_requests_get)
def test_ensemble_model(mock_get):
    ens_model = EnsembleModel(get_ensemble_url("1"))
    assert len(ens_model.children) == 1
    assert ens_model.children[0]._name == "default_smoother_update"
    assert ens_model._name == "default"
    assert len(ens_model.responses) == 1
