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


class MockDataLoader():
    def json(self, path: str) -> pd.DataFrame:
        return ensembles_response[path]


@pytest.fixture
def data_loader(mocker):
    dl = MockDataLoader()
    mocker.patch("ertviz.data_loader.data_loader", side_effect=lambda _: dl)
    return dl


def _pandas_read_csv(*args, **kwargs):
    data = args[0]
    if "header" in kwargs:
        return pd.DataFrame(data=list(data), columns=kwargs["header"])
    return pd.DataFrame(data=list(data), columns=["value"])


def _requests_get(url, **kwargs):
    class MockResponse:
        def __init__(self, data, status_code):
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

        def raise_for_status(self):
            if self.status_code == 400:
                raise HTTPError(
                    "Mocked requests raised HTTPError 400 due to missing data in test-data set!\n"
                    f"{args[0]}"
                )

    if url in ensembles_response:
        return MockResponse(ensembles_response[url], 200)
    return MockResponse({}, 400)


def _response_url(ensemble_id, response_id, project_id=None):
    return f"http://127.0.0.1:5000/ensembles/{ensemble_id}/responses/{response_id}"


def _parameter_data_url(ensemble_id, parameter_id, project_id=None):
    return (
        f"http://127.0.0.1:5000/ensembles/{ensemble_id}/parameters/{parameter_id}/data"
    )
