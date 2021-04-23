import os
import json
from typing import Any, Union, Mapping, Optional, List, MutableMapping, Tuple
from collections import defaultdict
from pprint import pformat
import requests
import logging
import pandas as pd
import io

logger = logging.getLogger()


def get_info(project_id: str = None) -> Mapping[str, str]:
    from ert_shared.storage.connection import get_info

    return get_info(project_id)


# these are needed to mock for testing
def _requests_get(*args: Union[str, bytes], **kwargs: Any) -> requests.models.Response:
    return requests.get(*args, **kwargs)


def _requests_post(*args: Union[str, bytes], **kwargs: Any) -> requests.models.Response:
    return requests.post(*args, **kwargs)


GET_REALIZATION = """\
query($ensembleId: ID!) {
  ensemble(id: $ensembleId) {
    name
    responses {
      name
      data_uri
    }
    parameters {
      name
      data_uri
    }
  }
}
"""

GET_ALL_ENSEMBLES = """\
query {
  experiments {
    name
    ensembles {
      id
      timeCreated
      parentEnsemble {
        id
      }
      childEnsembles {
        id
      }
    }
  }
}
"""

GET_ENSEMBLE = """\
query ($id: ID!) {
  ensemble(id: $id) {
    id
    size
    timeCreated
    children {
      ensembleResult{
        id
      }
    }
    Metadata
    parent {
      ensembleReference{
        id
      }
    }
    experiment {
      id
    }
  }
}
"""


data_cache: dict = {}
ServerIdentifier = Tuple[str, Optional[str]]  # (baseurl, optional token)


class DataLoaderException(Exception):
    pass


class DataLoader:
    _instances: MutableMapping[ServerIdentifier, "DataLoader"] = {}

    baseurl: str
    token: str
    _graphql_cache: MutableMapping[str, MutableMapping[dict, Any]]

    def __new__(cls, baseurl: str, token: Optional[str] = None) -> "DataLoader":
        if (baseurl, token) in cls._instances:
            return cls._instances[(baseurl, token)]

        loader = super().__new__(cls)
        loader.baseurl = baseurl
        loader.token = token
        loader._graphql_cache = defaultdict(dict)
        cls._instances[(baseurl, token)] = loader
        return loader

    def _query(self, query: str, **kwargs: Any) -> dict:
        """
        Cachable GraphQL helper
        """
        # query_cache = self._graphql_cache[query].get(kwargs)
        # if query_cache is not None:
        #     return query_cache
        resp = _requests_post(
            f"{self.baseurl}/gql",
            json={
                "query": query,
                "variables": kwargs,
            },
        )
        try:
            doc = resp.json()
        except json.JSONDecodeError:
            doc = resp.content
        if resp.status_code != 200 or isinstance(doc, bytes):
            raise RuntimeError(
                f"ERT Storage query returned with '{resp.status_code}':\n{pformat(doc)}"
            )

        # self._graphql_cache[query][kwargs] = doc
        # print(f"--- Query ---\n{query}\n--- Response ---\n{pformat(doc)}\n---------\n")
        return doc["data"]

    def _get(
        self, url: str, headers: dict = None, params: dict = None
    ) -> requests.Response:
        resp = _requests_get(f"{self.baseurl}/{url}", headers=headers, params=params)
        if resp.status_code != 200:
            raise DataLoaderException(
                f"""Error fetching data from {self.baseurl}/{url}
                The request return with status code: {resp.status_code}
                {str(resp.content)}
                """
            )
        return resp

    def get_all_ensembles(self) -> list:
        experiments = self._query(GET_ALL_ENSEMBLES)["experiments"]
        return [
            {"name": exp["name"], **ens}
            for exp in experiments
            for ens in exp["ensembles"]
        ]

    def get_ensemble(self, ensemble_id: str) -> dict:
        return self._query(GET_ENSEMBLE, id=ensemble_id)["ensemble"]

    def get_ensemble_responses(self, ensemble_id: str) -> dict:
        return self._get(url=f"ensembles/{ensemble_id}/responses").json()

    def get_ensemble_metadata(self, ensemble_id: str) -> dict:
        return self._get(url=f"ensembles/{ensemble_id}/metadata").json()

    def get_ensemble_parameters(self, ensemble_id: str) -> list:
        return self._get(url=f"ensembles/{ensemble_id}/parameters").json()

    def get_experiment_priors(self, experiment_id: str) -> dict:
        return self._get(url=f"experiments/{experiment_id}/priors").json()

    def get_ensemble_parameter_data(
        self, ensemble_id: str, parameter_name: str
    ) -> pd.DataFrame:
        resp = self._get(
            url=f"ensembles/{ensemble_id}/records/{parameter_name}",
            headers={"accept": "application/x-dataframe"},
        )
        stream = io.BytesIO(resp.content)
        df = pd.read_csv(stream, index_col=0, float_precision="round_trip")
        return df

    def get_ensemble_record_data(
        self, ensemble_id: str, record_name: str, ensemble_size: int
    ) -> pd.DataFrame:
        dfs = []
        for rel_idx in range(ensemble_size):
            try:
                resp = self._get(
                    url=f"ensembles/{ensemble_id}/records/{record_name}",
                    headers={"accept": "application/x-dataframe"},
                    params={"realization_index": rel_idx},
                )
                stream = io.BytesIO(resp.content)
                df = pd.read_csv(
                    stream, index_col=0, float_precision="round_trip"
                ).transpose()
                df.columns = [rel_idx]
                dfs.append(df)

            except DataLoaderException as e:
                logger.error(e)

        if dfs == []:
            raise DataLoaderException(f"No data found for {record_name}")

        return pd.concat(dfs, axis=1)

    def get_ensemble_record_observations(
        self, ensemble_id: str, record_name: str
    ) -> List[dict]:
        return self._get(
            url=f"ensembles/{ensemble_id}/records/{record_name}/observations",
            # Hard coded to zero, as all realizations are connected to the same observations
            params={"realization_index": 0},
        ).json()

    def compute_misfit(
        self, ensemble_id: str, response_name: str, summary: bool
    ) -> pd.DataFrame:
        resp = self._get(
            "compute/misfits",
            params={
                "ensemble_id": ensemble_id,
                "response_name": response_name,
                "summary_misfits": summary,
            },
        )
        stream = io.BytesIO(resp.content)
        df = pd.read_csv(stream, index_col=0, float_precision="round_trip")
        return df


def get_data_loader(project_id: Optional[str] = None) -> DataLoader:
    return DataLoader(*(get_info(project_id).values()))


def get_ensembles(project_id: Optional[str] = None) -> list:
    return get_data_loader(project_id).get_all_ensembles()
