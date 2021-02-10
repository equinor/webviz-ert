from datetime import datetime
from typing import List, Optional, Union
import pandas as pd
from ertviz.data_loader import DataLoader
from ertviz.models import Realization, Observation
from pydantic import BaseModel


class Indices(BaseModel):
    data: Union[List[float], List[datetime]]


class Response(BaseModel):
    id: int
    ensemble_id: int
    name: str
    axis: Indices

    _data_loader: Optional[DataLoader] = None
    _cached_data: Optional[pd.DataFrame] = None

    @staticmethod
    def from_data_loader(data_loader: DataLoader, ensemble_id: str, response_id: int) -> "Response":
        model = Response(**data_loader.json(f"/ensembles/{ensemble_id}/responses/{response_id}"))
        model._data_loader = data_loader
        return model

    @property
    def data_loader(self) -> DataLoader:
        if self._data_loader is None:
            raise ValueError(
                "No DataLoader provided: instantiate Response using from_data_loader"
            )
        return self._data_loader

    @property
    def data(self) -> pd.DataFrame:
        if self._cached_data is None:
            path = f"/ensembles/{self.ensemble_id}/responses/{self.id}/data"
            self._cached_data = self.data_loader.csv(path).T
            self._cached_data.columns = [real.name for real in self.realizations]
        return self._cached_data

    def univariate_misfits_df(self, selection=None):
        if selection is not None:
            data = {
                realization.name: realization.univariate_misfits_df["value_sign"]
                for realization in self.realizations
                if realization.name in selection
                and realization.univariate_misfits_df is not None
            }
        else:
            data = {
                realization.name: realization.univariate_misfits_df["value_sign"]
                for realization in self.realizations
                if realization.univariate_misfits_df is not None
            }
        if bool(data):
            misfits_df = pd.DataFrame(data=data)
            misfits_df["x_axis"] = self.realizations[0].univariate_misfits_df[
                "obs_location"
            ]
            if misfits_df["x_axis"].dtype == "object":
                misfits_df["x_axis"] = pd.to_datetime(
                    misfits_df["x_axis"], infer_datetime_format=True
                )
            misfits_df.index.name = self.name
            return misfits_df
        return None

    def summary_misfits_df(self, selection=None):
        if bool(selection):
            data = {
                realization.name: [realization.summarized_misfits_value]
                for realization in self.realizations
                if realization.name in selection
                and bool(realization.summarized_misfits_value)
            }
        else:
            data = {
                realization.name: [realization.summarized_misfits_value]
                for realization in self.realizations
                if bool(realization.summarized_misfits_value)
            }
        if bool(data):
            misfits_df = pd.DataFrame(data=data)
            misfits_df.index.name = self.name
            return misfits_df.astype("float64")
        return None

    def data_df(self, selection=None):
        if selection is not None:
            data = {
                realization.name: realization.data
                for realization in self.realizations
                if realization.name in selection
            }
        else:
            data = {
                realization.name: realization.data for realization in self.realizations
            }
        return pd.DataFrame(data=data).astype("float64")

    @property
    def realizations(self):
        self._update_schema()
        if "realizations" in self._schema:
            self._realizations_schema = self._schema["realizations"]

        if self._realizations is None:
            self._realizations = []
            for realization_schema in self._realizations_schema:
                self._realizations.append(
                    Realization(realization_schema=realization_schema)
                )
        return self._realizations
