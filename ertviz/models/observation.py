import pandas as pd
from ertviz.models import indexes_to_axis


class Observation:
    def __init__(self, observation_schema):
        self.name = str(observation_schema["name"])
        self._x_axis = []
        self._std = []
        self._values = []
        if "data" in observation_schema:
            data = observation_schema["data"]
            self._x_axis = data["x_axis"]["data"]
            self._std = data["std"]["data"]
            self._values = data["values"]["data"]

    def data_df(self):
        return pd.DataFrame(
            data={
                "values": self._values,
                "std": self._std,
                "x_axis": indexes_to_axis(self._x_axis),
            }
        )
