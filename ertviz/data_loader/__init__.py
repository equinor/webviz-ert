import os
import requests
import logging
import pandas


def get_info(project_id=None):
    from ert_shared.storage.connection import get_info

    return get_info(project_id)


os.environ["NO_PROXY"] = "localhost,127.0.0.1"
data_cache = {}


def get_url(project_id=None):
    return get_info(project_id)["baseurl"]


def get_auth(project_id=None):
    return get_info(project_id)["auth"]


def get_csv_data(data_url, project_id=None):
    response = requests.get(data_url, auth=get_auth(project_id), stream=True)
    return pandas.read_csv(response.raw, names=["value"])


def get_ensembles(project_id=None):
    server_url = get_url(project_id)
    data_cache["ensembles"] = get_schema(f"{server_url}/ensembles", project_id)[
        "ensembles"
    ]
    return data_cache["ensembles"]


def get_ensemble_url(ensemble_id, project_id=None):
    server_url = get_url(project_id)
    url = f"{server_url}/ensembles/{ensemble_id}"
    return url


def get_schema(api_url, project_id=None):
    logging.info(f"Getting json from {api_url}...")
    http_response = requests.get(api_url, auth=get_auth(project_id))
    http_response.raise_for_status()

    logging.info(" done!")
    return http_response.json()
