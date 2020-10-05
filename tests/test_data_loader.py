from ertviz.data_loader import DataLoader


def test_get_ensembles(data_loader):
    ensembles = data_loader.get_ensembles()
    assert len(ensembles) == 2


def test_get_ensemble(data_loader):
    ensemble = data_loader.get_ensemble("0")
    assert ensemble["name"] == "default"
