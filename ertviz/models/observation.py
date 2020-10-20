import pandas as pd
from ertviz.data_loader import get_data, get_numeric_data
from ertviz.models import indexes_to_axis


class Observation:
    def __init__(self, observation_schema):
        self.name = str(observation_schema["name"])
        self._data_indexes = []
        self._key_indexes = []
        self._std = []
        self._values = []
        if "data" in observation_schema:
            data = observation_schema["data"]
            self._data_indexes_url = data["data_indexes"]["data_url"]
            self._data_indexes = None
            self._key_indexes_url = data["key_indexes"]["data_url"]
            self._key_indexes = None
            self._std_url = data["std"]["data_url"]
            self._std = None
            self._values_url = data["values"]["data_url"]
            self._values = None

    def data_df(self):
        return pd.DataFrame(
            data={
                "values": self.values,
                "std": self.std,
                "x_axis": self.data_indexes_as_axis,
            }
        )

    @property
    def data_indexes(self):
        if self._data_indexes is None:
            self._data_indexes = get_data(self._data_indexes_url)
        return self._data_indexes

    @property
    def data_indexes_as_axis(self):
        return indexes_to_axis(self.data_indexes)

    @property
    def key_indexes(self):
        if self._key_indexes is None:
            self._key_indexes = get_data(self._key_indexes_url)
        return self._key_indexes

    @property
    def std(self):
        if self._std is None:
            self._std = get_numeric_data(self._std_url)
        return self._std

    @property
    def values(self):
        if self._values is None:
            self._values = get_numeric_data(self._values_url)
        return self._values
