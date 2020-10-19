import os
import requests
from datetime import datetime
import logging
import pandas


os.environ["NO_PROXY"] = "localhost,127.0.0.1"

data_cache = {}


def get_data(data_url):
    logging.info(f"Getting data from {data_url}...")
    http_response = requests.get(data_url)
    http_response.raise_for_status()

    logging.info(" done!")
    return http_response.text.split(",")


def get_numeric_data(data_url):
    data = get_data(data_url)
    return [eval(d) for d in data]


def get_csv_data(data_url):
    return pandas.read_csv(data_url, names=["value"])


def get_ensembles():
    server_url = "http://127.0.0.1:5000"
    data_cache["ensembles"] = get_schema(f"{server_url}/ensembles")["ensembles"]
    return data_cache["ensembles"]


def get_ensemble_url(ensemble_id):
    server_url = "http://127.0.0.1:5000"
    url = f"{server_url}/ensembles/{ensemble_id}"
    return url


def get_schema(api_url):
    logging.info(f"Getting json from {api_url}...")
    http_response = requests.get(api_url)
    http_response.raise_for_status()

    logging.info(" done!")
    return http_response.json()
