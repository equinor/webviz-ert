import pytest
import pandas as pd
from requests import HTTPError

from tests.data.snake_oil_data import ensembles_response
from selenium.webdriver.chrome.options import Options


def pytest_setup_options():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-setuid-sandbox")
    return options


@pytest.fixture
def mock_data(mocker):
    mocker.patch(
        "webviz_ert.data_loader.get_info",
        side_effect=lambda _: {"baseurl": "http://127.0.0.1:5000", "auth": ""},
    )

    mocker.patch("webviz_ert.data_loader._requests_get", side_effect=_requests_get)
    mocker.patch("webviz_ert.data_loader._requests_post", side_effect=_requests_post)


class _MockResponse:
    def __init__(self, url, data, status_code):
        self.data = data
        self.status_code = status_code

    def json(self):
        return self.data

    @property
    def text(self):
        return self.data

    @property
    def raw(self):
        return self.data

    @property
    def content(self):
        return self.data

    def raise_for_status(self):
        if self.status_code == 400:
            raise HTTPError(
                "Mocked requests raised HTTPError 400 due to missing data in test-data set!\n"
                f"{url}"
            )


def _requests_get(url, **kwargs):
    if kwargs.get("params") is not None:
        url += "?"
        for param, value in kwargs["params"].items():
            url += f"{param}={value}"
    if url in ensembles_response:
        return _MockResponse(url, ensembles_response[url], 200)
    return _MockResponse(url, {}, 400)


from webviz_ert.data_loader import GET_ENSEMBLE


def _requests_post(url, **kwargs):
    payload = kwargs["json"]
    if payload["query"] == GET_ENSEMBLE:
        variables = payload["variables"]
        ensemble_id = variables["id"]
        url = f"http://127.0.0.1:5000/ensembles/{ensemble_id}"

    if url in ensembles_response:
        return _MockResponse(url, ensembles_response[url], 200)
    return _MockResponse(url, {}, 400)
