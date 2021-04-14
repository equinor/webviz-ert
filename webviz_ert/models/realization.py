from typing import List, Optional
import pandas as pd
import math


class Realization:
    def __init__(self, realization_schema: dict):
        self._name = realization_schema["name"]
        self._data = realization_schema["data"]
        self._univariate_misfits_df = self._extract_univariate_misfits(
            realization_schema.get("univariate_misfits")
        )

    def _extract_univariate_misfits(
        self, schema: Optional[dict]
    ) -> Optional[pd.DataFrame]:
        if not schema:
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

    @property
    def summarized_misfits_value(self) -> float:
        return self.univariate_misfits_df["value"].sum()

    @property
    def univariate_misfits_df(self) -> pd.DataFrame:
        return self._univariate_misfits_df

    @property
    def data(self) -> List[float]:
        return self._data

    @property
    def name(self) -> str:
        return self._name
