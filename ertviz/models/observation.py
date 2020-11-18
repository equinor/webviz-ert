import pandas as pd
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
            self.data_indexes = data["data_indexes"]["data"]
            self.key_indexes = data["key_indexes"]["data"]
            self.std = data["std"]["data"]
            self.values = data["values"]["data"]

    def data_df(self):
        return pd.DataFrame(
            data={
                "values": self.values,
                "std": self.std,
                "x_axis": indexes_to_axis(self.key_indexes),
            }
        )

    @property
    def data_indexes_as_axis(self):
        return indexes_to_axis(self.data_indexes)
