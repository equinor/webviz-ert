from collections import namedtuple
import ertviz.ertapi.ensemble
import pandas as pd


class ParametersDict:
    def __init__(self, field, key, parent):
        self._field = field
        self._parent = parent
        self._key = key
        self._index = -1

    def __iter__(self):
        return self

    def _get_gen_class(self):
        return {
            "parameters": ertviz.ertapi.ensemble.Parameter,
            "observations": ertviz.ertapi.ensemble.Observation,
            "realizations": ertviz.ertapi.ensemble.Realization,
            "responses": ertviz.ertapi.ensemble.Response,
            "parameter_realizations": ertviz.ertapi.ensemble.ParameterRealization,
        }[self._field]

    def __next__(self):
        nodes = [node for node in self._parent.metadata[self._field]]
        self._index += 1
        if self._index < len(nodes):
            GenClass = self._get_gen_class()
            return GenClass(self._parent._request_handler, nodes[self._index])
        raise StopIteration

    def __getitem__(self, idx):
        GenClass = self._get_gen_class()
        for node in self._parent.metadata[self._field]:
            if idx == node[self._key]:
                return GenClass(self._parent._request_handler, node)
        return None

    def __getattr__(self, attr):
        return [node[attr] for node in self._parent.metadata[self._field]]


class RequestData:
    def __init__(self, request_handler, metadata_dict=None):
        self._metadata = metadata_dict
        self._request_handler = request_handler
        self._clear_data()
        self.load_metadata()

    def _clear_data(self):
        self._realizations = {}
        self._responses = {}
        self._parameters = {}
        self._observations = {}

    def get_node_fields(self, field, key=None):
        if field in self.metadata:
            if key is None:
                return self.metadata[field]
            if not isinstance(key, list):
                key = [key]
            Record = namedtuple(field, key)
            return Record(
                *[[node[val] for node in self.metadata[field]] for val in key]
            )

        return None

    @property
    def parameters(self):
        return ParametersDict("parameters", "key", self)

    @property
    def responses(self):
        return ParametersDict("responses", "name", self)

    @property
    def realizations(self):
        return ParametersDict("realizations", "name", self)

    @property
    def observations(self):
        return ParametersDict("observations", "name", self)

    @property
    def metadata(self):
        return self._metadata

    @property
    def data(self):
        return self._get_data()

    @property
    def name(self):
        if self.metadata is None or "name" not in self.metadata:
            return None
        return self.metadata["name"]

    def load_metadata(self):
        if self.metadata is not None and "ref_url" in self.metadata:
            self.req_metadata(self.metadata["ref_url"])

    def _get_data(self):
        if "data_url" in self.metadata:
            return self.req_data(self.metadata["data_url"])
        elif "alldata_url" in self.metadata:
            return self.req_alldata(self.metadata["alldata_url"])
        return None

    def req_metadata(self, ref_url):
        _metadata = self._request_handler.request(ref_url=ref_url, json=True)
        if _metadata is not None:
            self._metadata.update(_metadata)

    def req_data(self, ref_url):
        _data = self._request_handler.request(ref_url)
        if _data is not None:
            _data = _data.content.decode()
            return [eval(d) for d in _data.split(",")]

    def req_alldata(self, ref_url):
        return pd.read_csv(ref_url)
