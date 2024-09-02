import datetime
from typing import Dict, List, Optional, Union

import pandas as pd

from webviz_ert.models import AxisType, indexes_to_axis


class Observation:
    def __init__(self, observation_schema: Dict):
        self.name = str(observation_schema["name"])
        self._x_axis = indexes_to_axis(observation_schema["x_axis"])
        self._std = observation_schema["errors"]
        self._values = observation_schema["values"]
        self._attributes = ""
        self._active = [True for _ in self._x_axis] if self._x_axis else []

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

    @property
    def axis(self) -> Optional[List[Union[int, str, datetime.datetime]]]:
        return self._x_axis

    @property
    def axis_type(self) -> Optional[AxisType]:
        if self.axis is None:
            return None
        if str(self.axis[0]).isnumeric():
            return AxisType.INDEX
        return AxisType.TIMESTAMP
