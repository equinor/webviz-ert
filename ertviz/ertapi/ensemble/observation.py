from datetime import datetime
from ertviz.ertapi.ensemble.request_data import RequestData


def _convertdate(dstring):
    return datetime.strptime(dstring, "%Y-%m-%d %H:%M:%S")


def indexes_to_axis(indexes):
    if indexes and ":" in indexes[0]:
        return list(map(_convertdate, indexes))
    return list(map(int, indexes))


class ObsParam(RequestData):
    def __init__(self, request_handler, metadata_dict):
        super().__init__(request_handler=request_handler, metadata_dict=metadata_dict)

    @property
    def data_as_axis(self):
        return indexes_to_axis(self.data)


def _convertdate(dstring):
    return datetime.strptime(dstring, "%Y-%m-%d %H:%M:%S")


def indexes_to_axis(indexes):
    # if indexes and ":" in indexes[0]:
    #     return list(map(_convertdate, indexes))
    return list(map(int, indexes))


params_keys = ["active_mask", "data_indexes", "key_indexes", "std", "values"]


class Observation(RequestData):
    def __init__(self, request_handler, metadata_dict):
        super().__init__(request_handler=request_handler, metadata_dict=metadata_dict)

    def load_metadata(self):
        super().load_metadata()

        self._obs_params = {
            key: ObsParam(
                request_handler=self._request_handler,
                metadata_dict=self.metadata["data"][key],
            )
            for key in params_keys
        }

    @property
    def active_mask(self):
        return self._obs_params["active_mask"]

    @property
    def data_indexes(self):
        return self._obs_params["data_indexes"]

    @property
    def key_indexes(self):
        return self._obs_params["key_indexes"]

    @property
    def std(self):
        return self._obs_params["std"]

    @property
    def values(self):
        return self._obs_params["values"]
