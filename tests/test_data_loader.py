from ertviz.data_loader import get_ensembles


def test_get_ensembles(mock_requests_handler):
    global REQUEST_HANDLER
    REQUEST_HANDLER = mock_requests_handler
    ens = get_ensembles()
    assert len(ens) == 2
