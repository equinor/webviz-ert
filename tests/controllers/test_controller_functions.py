from webviz_ert.models.ensemble_model import EnsembleModel
from webviz_ert.controllers.controller_functions import (
    response_options,
    _valid_response_option,
)


def test_response_options(mock_data):
    ensemble3 = EnsembleModel(ensemble_id=3, project_id=None)
    ensemble4 = EnsembleModel(ensemble_id=4, project_id=None)

    options = response_options(response_filters=[], ensembles=[ensemble3, ensemble4])
    options_with_obs = response_options(
        response_filters=["obs"], ensembles=[ensemble3, ensemble4]
    )

    assert len(options) == 3
    assert len(options_with_obs) == 2


def test_valid_response_option():
    response_filters = ["obs", "historical"]

    class Response:
        name = "DummyResponse"
        observations = ["DummyObs"]

    response = Response()
    assert _valid_response_option(response_filters, response) is True

    response.name = "DummyResponseH"
    assert _valid_response_option(response_filters, response) is False

    response.name = "DummyResponseH:OP_1"
    assert _valid_response_option(response_filters, response) is False

    response.observations = []
    assert _valid_response_option(response_filters, response) is False

    response.name = "DummyResponse"
    response.observations = None
    assert _valid_response_option(response_filters, response) is False

    response_filters = ["obs"]
    response.name = "DummyResponseH"
    response.observations = ["DummyObs"]
    assert _valid_response_option(response_filters, response) is True

    response_filters = ["obs"]
    response.name = "DummyResponseH"
    response.observations = None
    assert _valid_response_option(response_filters, response) is False

    response_filters = ["historical"]
    response.name = "DummyResponse"
    response.observations = []
    assert _valid_response_option(response_filters, response) is True

    response_filters = ["historical"]
    response.name = "DummyResponseH"
    response.observations = []
    assert _valid_response_option(response_filters, response) is False
