from webviz_ert.data_loader import get_ensembles, refresh_data


def test_get_ensembles(tmp_path, mock_data):
    ensembles = get_ensembles(project_id=tmp_path)
    assert [ensemble["id"] for ensemble in ensembles] == [1, 2, 3, 42]


def test_refresh_data(tmp_path, mock_data):
    resp = refresh_data(project_id=tmp_path)
    assert resp.status_code == 200
