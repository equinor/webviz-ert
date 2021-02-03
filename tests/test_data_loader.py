from ertviz.data_loader import get_ensembles


def test_get_ensembles(mock_data):
    ens = get_ensembles()
    assert len(ens) == 2
