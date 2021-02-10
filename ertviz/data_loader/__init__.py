import os
import requests
import logging

from pathlib import Path
from typing import Any, Union
import pandas as pd

from ert_shared.storage.connection import get_info
from ert_shared.storage import paths


DATA_LOADERS = {}


class DataLoader:
    def __init__(self, project: Union[Path, str]) -> None:
        sys.exit(1)
        self._cache = {}

        conn_info = get_info(project)
        self._baseurl = conn_info["baseurl"]
        self._auth = conn_info["auth"]

    def get(self, path: str, **kwargs) -> requests.Response:
        resp = requests.get(f"{self._baseurl}/{path}", auth=self._auth, **kwargs)
        resp.raise_for_status()
        return resp

    def csv(self, path: str) -> pd.DataFrame:
        resp = self.get(path, stream=True)
        return pd.read_csv(resp.raw, names=["value"])

    def json(self, path: str) -> Any:
        return self.get(path).json()


def data_loader(project: str) -> DataLoader:
    """
    Cached DataLoader
    """
    if project in DATA_LOADERS:
        return DATA_LOADERS[project]
    DATA_LOADERS[project] = DataLoader(project)
    return DATA_LOADERS[project]
