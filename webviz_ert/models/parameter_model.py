import pandas as pd
from typing import List, Any, Optional, Union
from webviz_ert.data_loader import get_data_loader


class PriorModel:
    def __init__(
        self,
        function: str,
        function_parameter_names: List[str],
        function_parameter_values: List[Union[float, int]],
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
        self._data_loader = get_data_loader(self._project_id)

    def data_df(self) -> pd.DataFrame:
        if self._data_df.empty:
            _data_df = self._data_loader.get_ensemble_parameter_data(
                ensemble_id=self._ensemble_id, parameter_name=self.key
            )
            if _data_df is not None:
                _data_df = _data_df.transpose()
                _data_df.index.name = self.key
                self._data_df = _data_df
        return self._data_df
