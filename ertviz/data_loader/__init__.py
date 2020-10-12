import os
import requests
from datetime import datetime
import logging
import pandas

from ertviz.ertapi.ensemble import Ensembles
from ertviz.ertapi.client.request_handler import RequestHandler


os.environ["NO_PROXY"] = "localhost,127.0.0.1"

data_cache = {}

all_ensembles = None


def get_ensembles():
    global all_ensembles
    if all_ensembles is None:
        url = {"ref_url": "http://127.0.0.1:5000/ensembles"}
        all_ensembles = Ensembles(request_handler=RequestHandler(), metadata_dict=url)
    return all_ensembles


def get_data(data_url):
    logging.info(f"Getting data from {data_url}...")
    http_response = requests.get(data_url)
    http_response.raise_for_status()

    logging.info(" done!")
    return http_response.text.split(",")


def get_numeric_data(data_url):
    data = get_data(data_url)
    return [eval(d) for d in data]


# def get_csv_data(data_url):
#     return pandas.read_csv(data_url, names=["value"])


# def get_ensembles():
#     server_url = "http://127.0.0.1:5000"
#     data_cache["ensembles"] = get_schema(f"{server_url}/ensembles")["ensembles"]
#     return data_cache["ensembles"]


# def get_ensemble(ensemble_id):
#     url = get_ensembles()[eval(ensemble_id)]["ref_url"]
#     return get_schema(url)


def get_schema(api_url):
    logging.info(f"Getting json from {api_url}...")
    http_response = requests.get(api_url)
    http_response.raise_for_status()

    logging.info(" done!")
    return http_response.json()


# import is here to prevent circular loader, should be fixed when deciding on "lazy-load"
# model or fully populated model
from ertviz.models.parameter_model import (
    PriorModel,
    ParameterRealizationModel,
    ParametersModel,
)


def get_parameters(ensemble_id):
    ens = get_ensemble(ensemble_id)
    parameters = {}
    for param in ens.get("parameters", []):
        group = param["group"]
        key = param["key"]
        prior = None
        if param["prior"]:
            prior = PriorModel(
                param["prior"]["function"],
                param["prior"]["parameter_names"],
                param["prior"]["parameter_values"],
            )

        realizations_schema = get_schema(param["ref_url"])
        realizations_data_df = get_csv_data(realizations_schema["alldata_url"])
        realizations = [
            ParameterRealizationModel(schema["name"], values[1]["value"])
            for schema, values in zip(
                realizations_schema["parameter_realizations"],
                realizations_data_df.iterrows(),
            )
        ]
        parameters[key] = ParametersModel(
            group=group, key=key, prior=prior, realizations=realizations
        )

    return parameters
