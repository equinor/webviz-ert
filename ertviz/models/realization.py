import pandas as pd
import math


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
        # this account for not None and empty dict
        if not bool(schema):
            return None

        misfits_list = []
        for _, misfits in schema.items():
            for misfits_instance in misfits:
                misfits_list.append(misfits_instance)

        df = pd.DataFrame(data=misfits_list)
        df["value_sign"] = df[["value", "sign"]].apply(
            lambda row: -1.0 * math.sqrt(row[0]) if row[1] else math.sqrt(row[0]),
            axis=1,
        )
        return df

    def _extract_summary_misfits(self, schema):
        if not bool(schema):
            return None
        misfits_ = list(schema.values())[0]
        return misfits_

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
