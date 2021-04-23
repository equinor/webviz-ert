from typing import Dict
import pandas as pd
from webviz_ert.models import indexes_to_axis


class Observation:
    def __init__(self, observation_schema: Dict):
        self.name = str(observation_schema["name"])
        self._x_axis = observation_schema["x_axis"]
        self._std = observation_schema["errors"]
        self._values = observation_schema["values"]
        self._attributes = ""
        self._active = [True for _ in self._x_axis]

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
