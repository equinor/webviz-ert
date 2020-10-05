import os
import requests


os.environ["NO_PROXY"] = "localhost,127.0.0.1"

data_cache = {}


def get_data(data_url):
    print(f"Getting data from {data_url}...", end="")
    data = requests.get(data_url).text.split(",")
    print(" done!")
    return data


def get_ensembles():
    server_url = "http://127.0.0.1:5000"
    data_cache["ensembles"] = get_schema(f"{server_url}/ensembles")["ensembles"]
    return data_cache["ensembles"]


def get_ensemble(ensemble_id):
    url = get_ensembles()[eval(ensemble_id)]["ref_url"]
    return get_schema(url)


def get_schema(api_url):
    print(f"Getting json from {api_url}...", end="")
    json = requests.get(api_url).json()
    print(" done!")
    return json
