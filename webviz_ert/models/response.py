from typing import List, Mapping, Optional, Any, Union, Dict
import datetime
import pandas as pd
from webviz_ert.data_loader import get_schema, get_response_url

from webviz_ert.models import Realization, Observation, indexes_to_axis


class Response:
    def __init__(self, name: str, response_id: int, ensemble_id: int):
        self._schema: Optional[Mapping[str, Any]] = None  # get_schema(api_url=ref_url)
        self._id = response_id
        self._ensemble_id = ensemble_id
        self.name = name
        self._axis: Optional[List[Union[int, str, datetime.datetime]]] = None
        self._data = None
        self._realizations: Optional[List[Realization]] = None
        self._observations: Optional[List[Observation]] = None

    def _update_schema(self) -> None:
        if not self._schema:
            self._schema = get_schema(
                api_url=get_response_url(
                    ensemble_id=self._ensemble_id, response_id=self._id
                )
            )

    @property
    def ensemble_id(self) -> int:
        return self._ensemble_id

    @property
    def axis(self) -> Optional[List[Union[int, str, datetime.datetime]]]:
        if self._axis is None:
            self._update_schema()
            if self._schema:
                indexes = self._schema["axis"]["data"]
            self._axis = indexes_to_axis(indexes)
        return self._axis

    @property
    def data(self) -> pd.DataFrame:
        self._update_schema()
        if self._schema:
            self._data_url = self._schema["alldata_url"]
            if self._data is None and self._realizations is not None:
                self._data = pd.read_csv(self._data_url, header=None).T
                if self._data:
                    self._data.columns = [
                        realization.name for realization in self._realizations
                    ]
        return self._data

    def univariate_misfits_df(
        self, selection: Optional[List[int]] = None
    ) -> pd.DataFrame:
        if not self.realizations:
            return None
        if selection:
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
        if data:
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

    def summary_misfits_df(self, selection: Optional[List[int]] = None) -> pd.DataFrame:
        if not self.realizations:
            return None
        if selection:
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

    def data_df(self, selection: Optional[List[int]] = None) -> pd.DataFrame:
        if self.realizations:
            if selection:
                data = {
                    realization.name: realization.data
                    for realization in self.realizations
                    if realization.name in selection
                }
            else:
                data = {
                    realization.name: realization.data
                    for realization in self.realizations
                }
        return pd.DataFrame(data=data).astype("float64")

    @property
    def realizations(self) -> Optional[List[Realization]]:
        self._update_schema()
        if self._schema:
            if "realizations" in self._schema:
                self._realizations_schema = self._schema["realizations"]

            if self._realizations is None:
                self._realizations = [
                    Realization(realization_schema=realization_schema)
                    for realization_schema in self._realizations_schema
                ]
        return self._realizations

    @property
    def observations(self) -> Optional[List[Observation]]:
        self._update_schema()
        if not self._schema or "observations" not in self._schema:
            return []
        _observations_schema = self._schema["observations"]
        if self._observations is None and _observations_schema is not None:
            self._observations = []
            for observation_schema in _observations_schema:
                self._observations.append(
                    Observation(observation_schema=observation_schema)
                )
        return self._observations
