import pandas as pd
from ertviz.data_loader import get_data, get_schema
from ertviz.models import Realization, Observation, indexes_to_axis


class Response:
    def __init__(self, ref_url):
        schema = get_schema(api_url=ref_url)
        self.name = schema["name"]
        self.ensemble_id = schema["ensemble_id"]
        self._axis_url = schema["axis"]["data_url"]
        self._axis = None
        self._data_url = schema["alldata_url"]
        self._data = None
        self._realizations = []
        self._observations = []
        if "realizations" in schema:
            self._realizations_schema = schema["realizations"]
            self._realizations = None
        if "observations" in schema:
            self._observations_schema = schema["observations"]
            self._observations = None

    @property
    def axis(self):
        if self._axis is None:
            indexes = get_data(self._axis_url)
            self._axis = indexes_to_axis(indexes)
        return self._axis

    @property
    def data(self):
        if self._data is None and self._realizations is not None:
            self._data = pd.read_csv(self._data_url, header=None).T
            self._data.columns = [
                realization.name for realization in self._realizations
            ]
        return self._data

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
        if self._realizations is None:
            self._realizations = []
            for realization_schema in self._realizations_schema:
                self._realizations.append(
                    Realization(realization_schema=realization_schema)
                )
        return self._realizations

    @property
    def observations(self):
        if self._observations is None:
            self._observations = []
            for observation_schema in self._observations_schema:
                self._observations.append(
                    Observation(observation_schema=observation_schema)
                )
        return self._observations
