from typing import Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import pandas as pd

from ertviz.data_loader import DataLoader
from ertviz.models import Response

from ertviz.models.parameter_model import (
    PriorModel,
    ParametersModel,
)


class Prior(BaseModel):
    function: str
    parameter_names: List[str]
    parameter_values: List[float]


class Parameter(BaseModel):
    id: int
    ensemble_id: int
    project_id: int
    group: str
    key: str
    prior: Optional[Prior] = None


class Response(BaseModel):
    id: int
    ensemble_id: int
    name: str


class Update(BaseModel):
    id: int
    algorithm: str


class Ensemble(BaseModel):
    id: int
    name: str
    _children: Field(List[Update], alias="children")
    _parent: Field(Optional[Update], alias="parent") = None
    time_created: datetime
    responses: List[Response]
    parameters: List[Parameter]

    _data_loader: Optional[DataLoader] = None
    _style: dict = {}

    @classmethod
    def from_data_loader(cls, data_loader: DataLoader, ensemble_id: int) -> "Ensemble":
        model = Ensemble(**data_loader.json(f"/ensembles/{ensemble_id}"))
        model._data_loader = data_loader
        return model

    @property
    def data_loader(self) -> DataLoader:
        if self._data_loader is None:
            raise ValueError(
                "No DataLoader provided: instantiate Ensemble using from_data_loader"
            )
        return self._data_loader

    @property
    def children(self) -> List["Ensemble"]:
        """
        Lazy loader for Ensemble children
        """
        if hasattr(self, "_cached_children"):
            return self._cached_children
        self._cached_children = [
            Ensemble.from_data_loader(self.data_loader, child.id)
            for child in self._children
        ]
        return self._cached_children

    @property
    def parent(self) -> Optional["Ensemble"]:
        """
        Lazy loader for Ensemble parent
        """
        if not self._parent:
            return None
        if hasattr(self, "_cached_parent"):
            return self._cached_parent
        self._cached_parent = Ensemble.from_data_loader(data_loader, self._parent.id)
        return self._cached_parent

    def parameters_df(self, parameter_list=None):
        if parameter_list is None:
            parameter_list = self.parameters
        data = {
            parameter: self.parameters[parameter].data_df().values.flatten()
            for parameter in parameter_list
        }
        return pd.DataFrame(data=data)

    def __str__(self):
        return f"{self.time_created.strftime('%Y-%m-%d %H:%M:%S')}, {self.name}"
