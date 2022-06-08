from webviz_ert.data_loader import get_ensembles, refresh_data, DataLoader


def test_get_ensembles(mock_data):
    ensembles = get_ensembles()
    assert [ensemble["id"] for ensemble in ensembles] == [1, 2, 3, 42]


def test_refresh_data(mock_data):
    resp = refresh_data()
    assert resp.status_code == 200
