import requests
import pytest


@pytest.fixture(scope="session")
def get_info():
    from ert.shared.services import Storage

    with Storage.start_server() as service:
        yield service.fetch_url(), service.fetch_auth()[1]


@pytest.fixture(scope="session")
def requests_get(get_info):
    base_url, token = get_info

    def req_get(url, headers=None, params=None):
        if headers is None:
            headers = {}
        resp = requests.get(
            f"{base_url}/{url}",
            headers={**headers, "Token": token},
            params=params,
        )
        return resp

    return req_get


@pytest.fixture(scope="session")
def get_experiment_dict(requests_get):
    experiments = requests_get("experiments").json()
    return experiments[0]


@pytest.fixture(scope="session")
def get_ensemble_id(get_experiment_dict):
    return get_experiment_dict["ensemble_ids"][0]
