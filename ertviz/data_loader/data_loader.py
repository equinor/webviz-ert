import requests
import logging


class DataLoader:
    def __init__(self, request_handler):
        self._request_handler = request_handler
        self._data_cache = {}

    def get_data(self, data_url):
        logging.info(f"Getting data from {data_url}...", end="")
        data = self._request_handler.get(data_url, text=True).split(",")
        logging.info("Done!")
        return data

    def get_ensembles(self):
        server_url = self._request_handler.base_url
        self._data_cache["ensembles"] = self.get_schema(f"{server_url}/ensembles")[
            "ensembles"
        ]
        return self._data_cache["ensembles"]

    def get_ensemble(self, ensemble_id):
        url = self.get_ensembles()[eval(ensemble_id)]["ref_url"]
        return self.get_schema(url)

    def get_schema(self, api_url):
        logging.info(f"Getting json from {api_url}...", end="")
        json = self._request_handler.get(api_url, json=True)
        logging.info("Done!")
        return json


class RequestHandler:
    def __init__(self, base_url):
        self.base_url = base_url

    def get(self, url, json=False, text=False):
        reply = None
        try:
            reply = requests.get(url)
        except requests.ConnectionError as e:
            logging.error(e)
            return None
        if reply.status_code == 200:
            if json:
                return reply.json()
            if text:
                return reply.text()
            return reply
        return None
