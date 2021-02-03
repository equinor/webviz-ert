from ertviz.models.ensemble_model import EnsembleModel
from ertviz.controllers.controller_functions import response_options


def test_response_options(mock_data):
    ensemble3 = EnsembleModel(ensemble_id=3, project_id=None)
    ensemble4 = EnsembleModel(ensemble_id=4, project_id=None)

    options = response_options(response_filters=[], ensembles=[ensemble3, ensemble4])
    options_with_obs = response_options(
        response_filters=["obs"], ensembles=[ensemble3, ensemble4]
    )

    assert len(options) == 3
    assert len(options_with_obs) == 2
