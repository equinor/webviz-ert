import pytest
from tests.data.snake_oil_data import ensembles_response, test_base_url
from ertviz.data_loader import DataLoader


class RequestHandlerMock:
    @property
    def base_url(self):
        return test_base_url

    def get(self, ref_url, json=False, text=False):
        if ref_url in ensembles_response:
            return ensembles_response[ref_url]
        raise ValueError("{} is not a valid request URL".format(ref_url))


@pytest.fixture
def data_loader():
    request_handler_mock = RequestHandlerMock()
    return DataLoader(request_handler=request_handler_mock)
