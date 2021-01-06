from ertviz.data_loader import (
    get_schema,
    get_csv_data,
    get_parameter_url,
    get_parameter_data_url,
)


class PriorModel:
    def __init__(self, function, function_parameter_names, function_parameter_values):

        self.function = function
        self.function_parameter_names = function_parameter_names
        self.function_parameter_values = function_parameter_values


class ParametersModel:
    def __init__(self, **kwargs):
        self._project_id = kwargs["project_id"]
        self.group = kwargs["group"]
        self.key = kwargs["key"]
        self.priors = kwargs["prior"]
        self._id = kwargs["param_id"]
        self._ensemble_id = kwargs["ensemble_id"]
        self._realizations = kwargs.get("realizations")
        self._data_df = None

    def data_df(self):
        if self._data_df is None:
            self._data_df = get_csv_data(
                get_parameter_data_url(
                    ensemble_id=self._ensemble_id, parameter_id=self._id
                ),
                project_id=self._project_id,
            ).T
            self._data_df.index.name = self.key
        return self._data_df
