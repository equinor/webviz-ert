from webviz_ert.models import EnsembleModel


def test_ensemble_model(mock_data):
    ens_model = EnsembleModel(ensemble_id=1, project_id=None)
    assert len(ens_model.children) == 1
    assert ens_model.children[0]._name == "default_smoother_update"
    assert ens_model._name == "default"
    assert len(ens_model.responses) == 1
