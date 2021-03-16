import pandas as pd
from typing import List, Any, Optional
from ertviz.data_loader import (
    get_csv_data,
    get_parameter_data_url,
)


class PriorModel:
    def __init__(
        self,
        function: str,
        function_parameter_names: List[str],
        function_parameter_values: List[str],
    ):

        self.function = function
        self.function_parameter_names = function_parameter_names
        self.function_parameter_values = function_parameter_values


class ParametersModel:
    def __init__(self, **kwargs: Any):
        self._project_id = kwargs["project_id"]
        self.group = kwargs["group"]
        self.key = kwargs["key"]
        self.priors = kwargs["prior"]
        self._id = kwargs["param_id"]
        self._ensemble_id = kwargs["ensemble_id"]
        self._realizations = kwargs.get("realizations")
        self._data_df = pd.DataFrame()

    def data_df(self) -> pd.DataFrame:
        if self._data_df.empty:
            _data_df = get_csv_data(
                get_parameter_data_url(
                    ensemble_id=self._ensemble_id, parameter_id=self._id
                ),
                project_id=self._project_id,
            )
            if _data_df is not None:
                _data_df = _data_df.transpose()
                _data_df.index.name = self.key
                self._data_df = _data_df
        return self._data_df
