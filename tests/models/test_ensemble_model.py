from ertviz.models import Ensemble


def test_ensemble_model(data_loader):
    ens_model = Ensemble.from_data_loader(data_loader, ensemble_id=1)
    assert len(ens_model.children) == 1
    assert ens_model.children[0]._name == "default_smoother_update"
    assert ens_model._name == "default"
    assert len(ens_model.responses) == 1
