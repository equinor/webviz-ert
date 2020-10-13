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


def get_ensembles(ens_id=None):
    global all_ensembles
    if all_ensembles is None:
        url = {"ref_url": "http://127.0.0.1:5000/ensembles"}
        all_ensembles = Ensembles(request_handler=RequestHandler(), metadata_dict=url)
    if ens_id is not None:
        if isinstance(ens_id, str):
            ens_id = eval(ens_id)
        return all_ensembles[ens_id]
    return all_ensembles

