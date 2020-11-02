from ertviz.data_loader import get_data, get_schema, get_csv_data
from ertviz.models import Response

from ertviz.models.parameter_model import (
    PriorModel,
    ParameterRealizationModel,
    ParametersModel,
)


def get_parameter_models(parameters_schema):
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
            group=group, key=key, prior=prior, schema_url=param["ref_url"]
        )
    return parameters


class EnsembleModel:
    def __init__(self, ref_url):
        self._schema = get_schema(api_url=ref_url)
        self._name = self._schema["name"]
        self._id = ref_url
        self._children = self._schema["children"]
        self._parent = self._schema["parent"]
        self.responses = {
            resp_schema["name"]: Response(
                name=resp_schema["name"], ref_url=resp_schema["ref_url"]
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
            EnsembleModel(ref_url=child["ref_url"]) for child in self._children
        ]
        return self._cached_children

    @property
    def parent(self):
        if not self._parent:
            return None
        if hasattr(self, "_cached_parent"):
            return self._cached_parent

        self._cached_parent = EnsembleModel(ref_url=self._parent["ref_url"])
        return self._cached_parent

    @property
    def parameters(self):
        if self._parameters is None:
            self._parameters = get_parameter_models(self._schema["parameters"])
        return self._parameters

    @property
    def id(self):
        return self._id
