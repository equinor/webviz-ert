from ertviz.controllers import time_series_controller
from tests.data.snake_oil_data import test_base_url


def test_get_axis(data_loader):
    time_series_controller.data_loader = data_loader
    ensemble_schema = data_loader.get_ensemble("0")
    responses = [
        {"label": response["name"], "value": response["ref_url"]}
        for response in ensemble_schema["responses"]
    ]

    response = data_loader.get_schema(responses[0]["value"])
    x_axis = time_series_controller._get_axis(response["axis"]["data_url"])

    assert x_axis == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
