import os
import requests

os.environ["NO_PROXY"] = "localhost,127.0.0.1"


def get_data(data_url):
    return list(map(float, requests.get(data_url).text.split(",")))


def get_ensembles():
    server_url = "http://127.0.0.1:5000"
    return requests.get(f"{server_url}/ensembles").json()["ensembles"]


def api_request(api_url):
    return requests.get(api_url).json()
