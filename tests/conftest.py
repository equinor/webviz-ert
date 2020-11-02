import sys
import pytest
import pandas as pd
from tests.data.snake_oil_data import ensembles_response
from requests import HTTPError
from unittest.mock import Mock, MagicMock


def mocked_get_info():
    return {"baseurl": "http://127.0.0.1:5000", "auth": ""}


def mocked_read_csv(*args, **kwargs):
    data_url = args[0]
    data = ensembles_response[data_url]
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
