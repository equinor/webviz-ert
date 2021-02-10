from datetime import datetime
from typing import List, Union
import pandas as pd
from pydantic import BaseModel


class Indices(BaseModel):
    data: Union[List[int], List[datetime]]


class Data(BaseModel):
    data: List[float]


class Observation(BaseModel):
    name: str
    data_indexes: Indices
    key_indexes: Indices
    std: Data
    values: Data

    def data_df(self) -> pd.DataFrame:
        return pd.DataFrame(
            data={
                "values": self.values,
                "std": self.std,
                "x_axis": self.key_indexes,
            }
        )
