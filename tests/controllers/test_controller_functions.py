from ertviz.models import Ensemble
from ertviz.controllers.controller_functions import response_options


def test_response_options(data_loader):
    ensemble3 = Ensemble.from_data_loader(data_loader, ensemble_id=3)
    ensemble4 = Ensemble.from_data_loader(data_loader, ensemble_id=4)

    options = response_options(response_filters=[], ensembles=[ensemble3, ensemble4])
    options_with_obs = response_options(
        response_filters=["obs"], ensembles=[ensemble3, ensemble4]
    )

    assert len(options) == 3
    assert len(options_with_obs) == 2
