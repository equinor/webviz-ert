import io
import json
import logging
import operator
from collections import defaultdict
from urllib.parse import quote
from typing import Any, Callable, List, Mapping, MutableMapping, Optional, Tuple
from uuid import UUID

import pandas as pd
import requests

logger = logging.getLogger()

connection_info_map: dict = {}


def escape(s: str) -> str:
    return quote(quote(s, safe=""))


def get_connection_info(project_id: str) -> Mapping[str, str]:
    from ert.shared.storage.connection import get_info

    if project_id not in connection_info_map:
        info = get_info(project_id)
        info["auth"] = info["auth"][1]
        connection_info_map[project_id] = info

    return connection_info_map[project_id]


# these are needed to mock for testing
def _requests_get(*args: Any, **kwargs: Any) -> requests.models.Response:
    return requests.get(*args, **kwargs)


def _requests_post(*args: Any, **kwargs: Any) -> requests.models.Response:
    return requests.post(*args, **kwargs)


data_cache: dict = {}
ServerIdentifier = Tuple[str, Optional[str]]  # (baseurl, optional token)


class DataLoaderException(Exception):
    pass


class DataLoader:
    _instances: MutableMapping[ServerIdentifier, "DataLoader"] = {}

    baseurl: str
    token: Optional[str]
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

    def _get(
        self, url: str, headers: Optional[dict] = None, params: Optional[dict] = None
    ) -> requests.Response:
        if headers is None:
            headers = {}

        resp = _requests_get(
            f"{self.baseurl}/{url}",
            headers={**headers, "Token": self.token},
            params=params,
        )
        if resp.status_code != 200:
            raise DataLoaderException(
                f"""Error fetching data from {self.baseurl}/{url}
                The request return with status code: {resp.status_code}
                {str(resp.content)}
                """
            )
        return resp

    def _post(
        self, url: str, headers: Optional[dict] = None, params: Optional[dict] = None
    ) -> requests.Response:
        if headers is None:
            headers = {}

        resp = _requests_post(
            f"{self.baseurl}/{url}",
            headers={**headers, "Token": self.token},
            params=params,
        )
        if resp.status_code != 200:
            raise DataLoaderException(
                f"""Error posting to {self.baseurl}/{url}
                The request returned status code: {resp.status_code}
                {str(resp.content)}
                """
            )
        return resp

    def get_all_ensembles(self) -> list:
        try:
            experiments = self._get(url=f"experiments").json()
            return [
                self.get_ensemble(ensemble_id)
                for experiment in experiments
                for ensemble_id in experiment["ensemble_ids"]
            ]
        except DataLoaderException as e:
            logger.error(e)
            return list()

    def get_ensemble(self, ensemble_id: str) -> dict:
        try:
            return self._get(url=f"ensembles/{ensemble_id}").json()
        except DataLoaderException as e:
            logger.error(e)
            return dict()

    def get_ensemble_responses(self, ensemble_id: str) -> dict:
        try:
            # Map to experiment ID
            ensemble_info = self.get_ensemble(ensemble_id)
            experiment_id = ensemble_info["experiment_id"]
            experiment_info = self._get(url=f"experiments/{experiment_id}").json()

            # Read response/ obs metadata
            responses = experiment_info["responses"]
            observations = experiment_info["observations"]

            # Expand gendatas to the @ notation
            response_map = {}
            for gendata in responses.get("gen_data", []):
                report_steps = gendata["filter_on"]["report_step"]
                response_key = gendata["response_key"]
                for report_step in report_steps:
                    legacy_gendata_key = f"{response_key}@{report_step}"
                    response_map[legacy_gendata_key] = {
                        "id": f"id={UUID(int=0)}",
                        "name": legacy_gendata_key,
                        "has_observations": bool(
                            observations.get("gen_data", {}).get(response_key)
                        ),
                        "userdata": {"data_origin": "GEN_DATA"},
                    }

            for smry in responses.get("summary", []):
                response_key = smry["response_key"]
                response_map[response_key] = {
                    "id": f"id={UUID(int=0)}",
                    "name": response_key,
                    "has_observations": bool(
                        observations.get("summary", {}).get(response_key)
                    ),
                    "userdata": {"data_origin": "Summary"},
                }

            return response_map

        except DataLoaderException as e:
            logger.error(e)
            return dict()

    def get_ensemble_userdata(self, ensemble_id: str) -> dict:
        try:
            return self._get(url=f"ensembles/{ensemble_id}/userdata").json()
        except DataLoaderException as e:
            logger.error(e)
            return dict()

    def get_ensemble_parameters(self, ensemble_id: str) -> list:
        try:
            ensemble_info = self.get_ensemble(ensemble_id)
            experiment_id = ensemble_info["experiment_id"]
            experiment_info = self._get(url=f"experiments/{experiment_id}").json()

            # Read response/ obs metadata
            parameters = experiment_info["parameters"]

            param_list = []
            for param_group, metadatas in parameters.items():
                for metadata in metadatas:
                    parameter_key = metadata["key"]
                    userdata = metadata["userdata"]
                    is_log = metadata["transformation"] in {"LOGNORMAL", "LOGUNIF"}
                    param_list.append(
                        {
                            "userdata": userdata,
                            "dimensionality": metadata["dimensionality"],
                            "name": (
                                f"LOG10_{parameter_key}"
                                if is_log
                                else f"{parameter_key}"
                            ),
                            "labels": [],
                        }
                    )

            return param_list
        except DataLoaderException as e:
            logger.error(e)
            return list()

    def get_experiment_priors(self, experiment_id: str) -> dict:
        try:
            experiment = self._get(url=f"experiments/{experiment_id}").json()
            return experiment["priors"]
        except RuntimeError as e:
            logger.error(e)
            return dict()

    def get_ensemble_parameter_data(
        self,
        ensemble_id: str,
        parameter_name: str,
    ) -> pd.DataFrame:
        try:
            if "::" in parameter_name:
                name, label = parameter_name.split("::", 1)
                params = {"label": label}
            else:
                name = parameter_name
                params = {}

            resp = self._get(
                url=f"ensembles/{ensemble_id}/parameters/{escape(name)}",
                headers={"accept": "application/x-parquet"},
                params=params,
            )
            stream = io.BytesIO(resp.content)
            df = pd.read_parquet(stream).transpose()
            return df
        except DataLoaderException as e:
            logger.error(e)
            return pd.DataFrame()

    def get_ensemble_record_data(
        self,
        ensemble_id: str,
        record_name: str,
    ) -> pd.DataFrame:
        try:
            if "@" in record_name:
                response_key, report_step = record_name.split("@", 1)
                resp = self._get(
                    url=f"ensembles/{ensemble_id}/responses/{escape(response_key)}",
                    params={"filter_on": json.dumps({"report_step": report_step})},
                    headers={"accept": "application/x-parquet"},
                )
            else:
                resp = self._get(
                    url=f"ensembles/{ensemble_id}/responses/{escape(record_name)}",
                    headers={"accept": "application/x-parquet"},
                )

            stream = io.BytesIO(resp.content)
            df = pd.read_parquet(stream).transpose()

        except DataLoaderException as e:
            logger.error(e)
            return pd.DataFrame()
        try:
            df.index = df.index.astype(int)
        except (TypeError, ValueError):
            try:
                df.index = df.index.map(pd.Timestamp)
            except ValueError:
                pass
        df = df.sort_index()
        return df

    def get_ensemble_record_observations(
        self, ensemble_id: str, record_name: str
    ) -> List[dict]:
        try:
            if "@" in record_name:
                response_key, _ = record_name.split("@", 1)
                return self._get(
                    url=f"ensembles/{ensemble_id}/responses/{escape(response_key)}/observations",
                    # Hard coded to zero, as all realizations are connected to the same observations
                    params={"realization_index": 0},
                ).json()
            else:
                return self._get(
                    url=f"ensembles/{ensemble_id}/responses/{escape(record_name)}/observations",
                    # Hard coded to zero, as all realizations are connected to the same observations
                    params={"realization_index": 0},
                ).json()
        except DataLoaderException as e:
            logger.error(e)
            return list()

    def compute_misfit(
        self, ensemble_id: str, response_name: str, summary: bool
    ) -> pd.DataFrame:
        try:

            if not summary:
                # assume gen data
                response_key, report_step = response_name.split("@", 1)
                resp = self._get(
                    "compute/misfits",
                    params={
                        "ensemble_id": ensemble_id,
                        "response_name": response_key,
                        "filter_on": json.dumps({"report_step": report_step}),
                        "summary_misfits": False,
                    },
                )
            else:
                resp = self._get(
                    "compute/misfits",
                    params={
                        "ensemble_id": ensemble_id,
                        "response_name": response_name,
                        "summary_misfits": True,
                    },
                )
            stream = io.BytesIO(resp.content)
            df = pd.read_csv(stream, index_col=0, float_precision="round_trip")
            return df
        except DataLoaderException as e:
            logger.error(e)
            return pd.DataFrame()

    def refresh_data(self) -> requests.Response:
        return self._post("updates/facade")


def get_data_loader(project_id: str) -> DataLoader:
    return DataLoader(*(get_connection_info(project_id).values()))


def get_ensembles(project_id: str) -> list:
    return get_data_loader(project_id).get_all_ensembles()


def refresh_data(project_id: str) -> requests.Response:
    return get_data_loader(project_id).refresh_data()
