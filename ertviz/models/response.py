import pandas as pd
from ertviz.data_loader import get_data, get_schema
from ertviz.models import Realization, Observation, indexes_to_axis


class Response:
    def __init__(self, name, ref_url):
        self._schema = None  # get_schema(api_url=ref_url)
        self._ref_url = ref_url
        self.name = name
        self._axis = None
        self._data = None
        self._realizations = []
        self._observations = []
        self._realizations = None
        self._observations = None

    def _update_schema(self):
        if not self._schema:
            self._schema = get_schema(api_url=self._ref_url)

    @property
    def ensemble_id(self):
        self._update_schema()
        return self._schema["ensemble_id"]

    @property
    def axis(self):
        self._update_schema()
        self._axis_url = self._schema["axis"]["data_url"]
        if self._axis is None:
            indexes = get_data(self._axis_url)
            self._axis = indexes_to_axis(indexes)
        return self._axis

    @property
    def data(self):
        self._update_schema()
        self._data_url = self._schema["alldata_url"]
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

    @property
    def observations(self):
        self._update_schema()
        if not "observations" in self._schema:
            return []
        _observations_schema = self._schema["observations"]
        if self._observations is None and _observations_schema is not None:
            self._observations = []
            for observation_schema in _observations_schema:
                self._observations.append(
                    Observation(observation_schema=observation_schema)
                )
        return self._observations
