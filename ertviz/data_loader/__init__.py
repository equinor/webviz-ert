import os
import requests
from datetime import datetime
import logging

os.environ["NO_PROXY"] = "localhost,127.0.0.1"

data_cache = {}


def get_data(data_url):
    logging.info(f"Getting data from {data_url}...", end="")
    http_response = requests.get(data_url)
    http_response.raise_for_status()

    logging.info(" done!")
    return http_response.text.split(",")


def get_numeric_data(data_url):
    data = get_data(data_url)
    return [eval(d) for d in data]


def get_ensembles():
    server_url = "http://127.0.0.1:5000"
    data_cache["ensembles"] = get_schema(f"{server_url}/ensembles")["ensembles"]
    return data_cache["ensembles"]


def get_ensemble(ensemble_id):
    url = get_ensembles()[eval(ensemble_id)]["ref_url"]
    return get_schema(url)


def get_schema(api_url):
    logging.info(f"Getting json from {api_url}...", end="")
    http_response = requests.get(api_url)
    http_response.raise_for_status()

    logging.info(" done!")
    return http_response.json()
