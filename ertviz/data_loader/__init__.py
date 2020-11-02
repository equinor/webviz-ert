import os
import requests
from datetime import datetime
import logging
import pandas
import json


def get_info():
    from ert_shared.storage.connection import get_info

    return get_info()


os.environ["NO_PROXY"] = "localhost,127.0.0.1"
data_cache = {}


def get_url():
    return get_info()["baseurl"]


def get_auth():
    return get_info()["auth"]


def get_data(data_url):
    logging.info(f"Getting data from {data_url}...")
    http_response = requests.get(data_url, auth=get_auth())
    http_response.raise_for_status()

    logging.info(" done!")
    return http_response.text.split(",")


def get_numeric_data(data_url):
    data = get_data(data_url)
    return [eval(d) for d in data]


def get_csv_data(data_url):
    response = requests.get(data_url, auth=get_auth(), stream=True)
    return pandas.read_csv(response.raw, names=["value"])


def get_ensembles():
    server_url = get_url()
    data_cache["ensembles"] = get_schema(f"{server_url}/ensembles")["ensembles"]
    return data_cache["ensembles"]


def get_ensemble_url(ensemble_id):
    server_url = get_url()
    url = f"{server_url}/ensembles/{ensemble_id}"
    return url


def get_schema(api_url):
    logging.info(f"Getting json from {api_url}...")
    http_response = requests.get(api_url, auth=get_auth())
    http_response.raise_for_status()

    logging.info(" done!")
    return http_response.json()
