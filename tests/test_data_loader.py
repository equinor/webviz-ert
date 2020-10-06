from ertviz.data_loader import DataLoader


def test_get_ensembles(data_loader):
    ensembles = data_loader.get_ensembles()
    assert len(ensembles) == 2


def test_get_ensemble(data_loader):
    ensemble = data_loader.get_ensemble("0")
    assert ensemble["name"] == "default"


def test_get_axis(data_loader):
    ensemble_schema = data_loader.get_ensemble("0")
    responses = [
        {"label": response["name"], "value": response["ref_url"]}
        for response in ensemble_schema["responses"]
    ]
    x_axis = data_loader.get_axis(responses[0]["value"])

    assert x_axis == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
