import pandas as pd
from requests import HTTPError

from tests.data.snake_oil_data import ensembles_response
from selenium.webdriver.chrome.options import Options


def pytest_setup_options():
    options = Options()
    options.add_argument("--headless")
    return options


def mocked_get_info(project_id):
    return {"baseurl": "http://127.0.0.1:5000", "auth": ""}


def mocked_read_csv(*args, **kwargs):
    data = args[0]
    if "header" in kwargs:
        return pd.DataFrame(data=list(data), columns=kwargs["header"])
    return pd.DataFrame(data=list(data), columns=["value"])


def mocked_requests_get(*args, **kwargs):
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

    if args[0] in ensembles_response:
        return MockResponse(ensembles_response[args[0]], 200)
    return MockResponse({}, 400)


def mocked_get_url():
    return "http://127.0.0.1:5000"


def mocked_get_auth():
    return ""


def mocked_get_ensemble_url(ensemble_id, project_id=None):
    return f"http://127.0.0.1:5000/ensembles/{ensemble_id}"


def mocked_get_response_url(ensemble_id, response_id, project_id=None):
    return f"http://127.0.0.1:5000/ensembles/{ensemble_id}/responses/{response_id}"


def mocked_get_parameter_data_url(ensemble_id, parameter_id, project_id=None):
    return (
        f"http://127.0.0.1:5000/ensembles/{ensemble_id}/parameters/{parameter_id}/data"
    )
