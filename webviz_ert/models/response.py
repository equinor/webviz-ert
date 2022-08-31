from typing import List, Mapping, Optional, Any
import pandas as pd
from webviz_ert.data_loader import get_data_loader, DataLoader

from webviz_ert.models import Observation, AxisType


class Response:
    def __init__(
        self,
        name: str,
        ensemble_id: str,
        project_id: str,
        ensemble_size: int,
        active_realizations: List[int],
        resp_schema: Any,
    ):
        self._data_loader: DataLoader = get_data_loader(project_id)
        self._document: Optional[Mapping[str, Any]] = None
        self._id: str = resp_schema["id"]
        self._ensemble_id: str = ensemble_id
        self.name: str = name
        self._data: Optional[pd.DataFrame] = None
        self._observations: Optional[List[Observation]] = None
        self._univariate_misfits_df: Optional[pd.DataFrame] = None
        self._summary_misfits_df: Optional[pd.DataFrame] = None
        self._ensemble_size: int = ensemble_size
        self._active_realizations: List[int] = active_realizations
        self._has_observations: bool = resp_schema.get("has_observations")

    @property
    def ensemble_id(self) -> str:
        return self._ensemble_id

    @property
    def axis(self) -> pd.Index:
        return self.data.index

    @property
    def axis_type(self) -> Optional[AxisType]:
        if self.axis is None or self.axis.empty:
            return None
        if str(self.axis[0]).isnumeric():
            return AxisType.INDEX
        return AxisType.TIMESTAMP

    @property
    def data(self) -> pd.DataFrame:
        if self._data is None:
            self._data = self._data_loader.get_ensemble_record_data(
                self._ensemble_id, self.name
            )
        return self._data

    @property
    def empty(self) -> bool:
        return self.data.empty

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

    @property
    def has_observations(self) -> bool:
        return self._has_observations
