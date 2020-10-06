from unittest import mock
from tests.conftest import mocked_requests_get
from ertviz.data_loader import get_ensembles, get_ensemble


@mock.patch("ertviz.data_loader.requests.get", side_effect=mocked_requests_get)
def test_get_ensembles(mock_get):
    ens = get_ensembles()
    assert len(ens) == 2


@mock.patch("ertviz.data_loader.requests.get", side_effect=mocked_requests_get)
def test_get_ensemble(mock_get):
    ensemble = get_ensemble("0")
    assert ensemble is not None
    assert ensemble["name"] == "default"
