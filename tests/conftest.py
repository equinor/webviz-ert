import pytest
from tests.data.snake_oil_data import ensembles_response


class RequestHandlerMock:
    def request(self, ref_url, json=False, stream=False):
        if ref_url in ensembles_response:
            return ensembles_response[ref_url]
        raise ValueError("{} is not a valid request URL".format(ref_url))


@pytest.fixture
def mock_requests_handler():
    return RequestHandlerMock()
