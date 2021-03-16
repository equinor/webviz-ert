from typing import Dict
import pandas as pd
from ertviz.models import indexes_to_axis


class Observation:
    def __init__(self, observation_schema: Dict):
        self.name = str(observation_schema["name"])
        self._x_axis = []
        self._std = []
        self._values = []
        self._attributes = ""
        self._active = []

        if "data" in observation_schema:
            data = observation_schema["data"]
            self._x_axis = data["x_axis"]["data"]
            self._std = data["std"]["data"]
            self._values = data["values"]["data"]
            self._active = data["active"]["data"]

        if "attributes" in observation_schema:
            for k, v in observation_schema["attributes"].items():
                self._attributes += f"{k}: {v}<br>"

    def data_df(self) -> pd.DataFrame:
        return pd.DataFrame(
            data={
                "values": self._values,
                "std": self._std,
                "x_axis": indexes_to_axis(self._x_axis),
                "attributes": self._attributes,
                "active": self._active,
            }
        )
