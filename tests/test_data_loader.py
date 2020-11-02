from unittest import mock
import tests.conftest
from tests.conftest import mocked_requests_get, mocked_get_info
from ertviz.data_loader import get_ensembles


@mock.patch("ertviz.data_loader.requests.get", side_effect=mocked_requests_get)
@mock.patch("ertviz.data_loader.get_info", side_effect=mocked_get_info)
def test_get_ensembles(mock_request_get, mock_get_info):
    ens = get_ensembles()
    assert len(ens) == 2
