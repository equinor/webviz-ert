import os
import requests


os.environ["NO_PROXY"] = "localhost,127.0.0.1"

def get_data(data_url):
    print(f"Getting data from {data_url}...", end="")
    data = list(map(float, requests.get(data_url).text.split(",")))
    print(" done!")
    return data 


def get_ensembles():
    server_url = "http://127.0.0.1:5000"
    return requests.get(f"{server_url}/ensembles").json()["ensembles"]


def api_request(api_url):
    print(f"Getting json from {api_url}...", end="")
    json = requests.get(api_url).json()
    print(" done!")
    return json
