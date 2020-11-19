import pandas as pd
from ertviz.data_loader import get_data


class Realization:
    def __init__(self, realization_schema):
        self._name = realization_schema["name"]
        self._data = realization_schema["data"]
        self._univariate_misfits_df = self._extract_univariate_misfits(
            realization_schema.get("univariate_misfits")
        )
        self._summarized_missfits_value = self._extract_summary_misfits(
            realization_schema.get("summarized_misfits")
        )

    def _extract_univariate_misfits(self, schema):
        if bool(schema):  # this account for not None and empty dict
            misfits_ = list(schema.values())
            return pd.DataFrame(misfits_[0])
        return None

    def _extract_summary_misfits(self, schema):
        if bool(schema):
            misfits_ = list(schema.values())[0]
            return misfits_
        return None

    @property
    def summarized_misfits_value(self):
        return self._summarized_missfits_value

    @property
    def univariate_misfits_df(self):
        return self._univariate_misfits_df

    @property
    def data(self):
        return self._data

    @property
    def name(self):
        return self._name
