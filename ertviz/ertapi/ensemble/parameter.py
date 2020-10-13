from ertviz.ertapi.ensemble.request_data import RequestData, ParametersDict
from ertviz.ertapi.ensemble.realization import Realization


class ParameterRealization(RequestData):
    def __init__(self, request_handler, metadata_dict):
        super().__init__(request_handler=request_handler, metadata_dict=metadata_dict)

    @property
    def realization(self):
        return Realization(self._request_handler, self.metadata["realization"])


class Parameter(RequestData):
    def __init__(self, request_handler, metadata_dict):
        super().__init__(request_handler=request_handler, metadata_dict=metadata_dict)

    @property
    def prior(self):
        return self.metadata["prior"]

    @property
    def parameter_realizations(self):
        # self.get_node_fields("parameter_realizations", key=["name"])
        return ParametersDict("parameter_realizations", "name", self)

    @property
    def group(self):
        return self.metadata["group"]

    @property
    def key(self):
        return self.metadata["key"]
