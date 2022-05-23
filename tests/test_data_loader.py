from webviz_ert.data_loader import get_ensembles, refresh_data


def test_get_ensembles(mock_data):
    ens = get_ensembles()
    assert len(ens) == 3


def test_refresh_data(mock_data):
    resp = refresh_data()
    assert resp.status_code == 200
