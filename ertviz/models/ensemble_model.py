import pandas as pd
from ertviz.data_loader import get_ensemble_url, get_schema
from ertviz.models import Response

from ertviz.models.parameter_model import (
    PriorModel,
    ParametersModel,
)


def get_parameter_models(parameters_schema, ensemble_id, project_id):
    parameters = {}
    for param in parameters_schema:
        group = param["group"]
        key = param["key"]
        prior = None
        if param["prior"]:
            prior = PriorModel(
                param["prior"]["function"],
                param["prior"]["parameter_names"],
                param["prior"]["parameter_values"],
            )
        parameters[key] = ParametersModel(
            group=group,
            key=key,
            prior=prior,
            param_id=param["id"],
            project_id=project_id,
            ensemble_id=ensemble_id,
        )
    return parameters


class EnsembleModel:
    def __init__(self, ensemble_id, project_id):
        self._schema = get_schema(get_ensemble_url(ensemble_id))
        self._project_id = project_id
        self._name = self._schema["name"]
        self._id = ensemble_id
        self._children = self._schema["children"]
        self._parent = self._schema["parent"]
        self._time_created = self._schema["time_created"]
        self.responses = {
            resp_schema["name"]: Response(
                name=resp_schema["name"],
                response_id=resp_schema["id"],
                ensemble_id=ensemble_id,
            )
            for resp_schema in self._schema["responses"]
        }
        self._parameters = None
        self.style = {}

    @property
    def children(self):
        if hasattr(self, "_cached_children"):
            return self._cached_children
        self._cached_children = [
            EnsembleModel(ensemble_id=child["id"], project_id=self._project_id)
            for child in self._children
        ]
        return self._cached_children

    @property
    def parent(self):
        if not self._parent:
            return None
        if hasattr(self, "_cached_parent"):
            return self._cached_parent

        self._cached_parent = EnsembleModel(
            ensemble_id=self._parent["id"], project_id=self._project_id
        )
        return self._cached_parent

    @property
    def parameters(self):
        if self._parameters is None:
            self._parameters = get_parameter_models(
                self._schema["parameters"],
                ensemble_id=self._id,
                project_id=self._project_id,
            )
        return self._parameters

    def parameters_df(self, parameter_list=None):
        if parameter_list is None:
            parameter_list = self.parameters
        data = {
            parameter: self.parameters[parameter].data_df().values.flatten()
            for parameter in parameter_list
        }
        return pd.DataFrame(data=data)

    @property
    def id(self):
        return self._id

    def __str__(self):
        if "." in self._time_created:
            return f"{self._time_created.split('.')[0]}, {self._name}"
        return f"{self._time_created}, {self._name}"

    def __repr__(self):
        return f"{self._name}"
