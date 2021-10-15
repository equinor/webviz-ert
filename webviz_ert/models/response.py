from typing import List, Mapping, Optional, Any, Union, Dict
import datetime
import pandas as pd
from webviz_ert.data_loader import get_data_loader, DataLoader

from webviz_ert.models import Realization, Observation, indexes_to_axis


class Response:
    def __init__(
        self,
        name: str,
        response_id: str,
        ensemble_id: str,
        project_id: str,
        ensemble_size: int,
        active_realizations: List[int],
    ):
        self._data_loader: DataLoader = get_data_loader(project_id)
        self._document: Optional[Mapping[str, Any]] = None
        self._id: str = response_id
        self._ensemble_id: str = ensemble_id
        self.name: str = name
        self._data: Optional[pd.DataFrame] = None
        self._observations: Optional[List[Observation]] = None
        self._univariate_misfits_df: Optional[pd.DataFrame] = None
        self._summary_misfits_df: Optional[pd.DataFrame] = None
        self._ensemble_size: int = ensemble_size
        self._active_realizations: List[int] = active_realizations

    @property
    def ensemble_id(self) -> str:
        return self._ensemble_id

    @property
    def axis(self) -> Optional[List[Union[int, str, datetime.datetime]]]:
        return self.data.index

    @property
    def data(self) -> pd.DataFrame:
        if self._data is None:
            self._data = self._data_loader.get_ensemble_record_data(
                self._ensemble_id, self.name, self._active_realizations
            )
        return self._data

    def univariate_misfits_df(
        self, selection: Optional[List[int]] = None
    ) -> pd.DataFrame:
        if self._univariate_misfits_df is None:
            self._univariate_misfits_df = self._data_loader.compute_misfit(
                self._ensemble_id, self.name, summary=False
            )
        if selection:
            return self._univariate_misfits_df.iloc[selection, :]
        return self._univariate_misfits_df

    def summary_misfits_df(self, selection: Optional[List[int]] = None) -> pd.DataFrame:
        if self._summary_misfits_df is None:
            self._summary_misfits_df = self._data_loader.compute_misfit(
                self._ensemble_id, self.name, summary=True
            )
        if selection:
            self._summary_misfits_df.iloc[selection, :]
        return self._summary_misfits_df

    def data_df(self, selection: Optional[List[int]] = None) -> pd.DataFrame:
        if selection:
            self.data.iloc[selection, :]
        return self.data

    @property
    def observations(self) -> Optional[List[Observation]]:
        if self._observations is None:
            _observations_schemas = self._data_loader.get_ensemble_record_observations(
                self._ensemble_id, self.name
            )
            self._observations = []
            for observation_schema in _observations_schemas:
                self._observations.append(
                    Observation(observation_schema=observation_schema)
                )
        return self._observations
