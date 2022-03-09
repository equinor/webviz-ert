import json
import pandas as pd
from typing import Mapping, List, Dict, Union, Any, Optional
from webviz_ert.data_loader import get_data_loader, DataLoaderException
from webviz_ert.models import Response, PriorModel, ParametersModel


def _create_parameter_models(
    parameters_names: list,
    priors: dict,
    ensemble_id: str,
    project_id: str,
) -> Optional[Mapping[str, ParametersModel]]:
    parameters = {}
    for param in parameters_names:
        key = param
        prior_schema = priors.get(key, None)
        prior = None
        if prior_schema:
            prior = PriorModel(
                prior_schema["function"],
                [x[0] for x in prior_schema.items() if isinstance(x[1], (float, int))],
                [x[1] for x in prior_schema.items() if isinstance(x[1], (float, int))],
            )

        parameters[key] = ParametersModel(
            group="",  # TODO?
            key=key,
            prior=prior,
            param_id="",  # TODO?
            project_id=project_id,
            ensemble_id=ensemble_id,
        )
    return parameters


class EnsembleModel:
    def __init__(self, ensemble_id: str, project_id: str) -> None:
        self._data_loader = get_data_loader(project_id)
        self._schema = self._data_loader.get_ensemble(ensemble_id)
        self._experiment_id = self._schema["experiment"]["id"]
        self._project_id = project_id
        self._metadata = json.loads(self._schema["userdata"])
        if "name" in self._metadata:
            self._name = self._metadata["name"]
        else:
            self._name = (
                f"{self._schema['experiment']['name']}-{self._schema['timeCreated']}"
            )
        self._id = ensemble_id
        self._children = self._schema["children"]
        self._parent = self._schema["parent"]
        self._size = self._schema["size"]
        self._active_realizations = self._schema["activeRealizations"]
        self._time_created = self._schema["timeCreated"]
        self._responses: Dict[str, Response] = {}
        self._parameters: Optional[Mapping[str, ParametersModel]] = None
        self._cached_children: Optional[List["EnsembleModel"]] = None
        self._cached_parent: Optional["EnsembleModel"] = None

    @property
    def responses(self) -> Dict[str, Response]:
        if not self._responses:
            self._responses = {}
            responses_dict = self._data_loader.get_ensemble_responses(self._id)
            response_names = list(responses_dict.keys())
            response_names.sort()

            for name in response_names:
                self._responses[name] = Response(
                    name=name,
                    ensemble_id=self._id,
                    project_id=self._project_id,
                    ensemble_size=self._size,
                    active_realizations=self._active_realizations,
                    resp_schema=responses_dict[name],
                )
        return self._responses

    @property
    def children(self) -> Optional[List["EnsembleModel"]]:
        if not self._cached_children:
            self._cached_children = [
                EnsembleModel(
                    ensemble_id=child["ensembleResult"]["id"],
                    project_id=self._project_id,
                )
                for child in self._children
            ]
        return self._cached_children

    @property
    def parent(self) -> Optional["EnsembleModel"]:
        if not self._parent:
            return None
        if not self._cached_parent:
            self._cached_parent = EnsembleModel(
                ensemble_id=self._parent["ensembleReference"]["id"],
                project_id=self._project_id,
            )
        return self._cached_parent

    @property
    def parameters(
        self,
    ) -> Optional[Mapping[str, ParametersModel]]:
        if not self._parameters:
            parameter_names = []
            for params in self._data_loader.get_ensemble_parameters(self._id):
                labels = params["labels"]
                param_name = params["name"]
                if len(labels) > 0:
                    for label in labels:
                        parameter_names.append(f"{param_name}::{label}")
                else:
                    parameter_names.append(param_name)
            parameter_priors = (
                self._data_loader.get_experiment_priors(self._experiment_id)
                if not self._parent
                else {}
            )
            self._parameters = _create_parameter_models(
                parameter_names,
                parameter_priors,
                ensemble_id=self._id,
                project_id=self._project_id,
            )
        return self._parameters

    def parameters_df(self, parameter_list: Optional[List[str]] = None) -> pd.DataFrame:
        if not self.parameters or not parameter_list:
            return None
        data = {
            parameter: self.parameters[parameter].data_df().values.flatten()
            for parameter in parameter_list
        }
        return pd.DataFrame(data=data)

    @property
    def id(self) -> str:
        return self._id

    def __str__(self) -> str:
        if "." in self._time_created:
            return f"{self._time_created.split('.')[0]}, {self._name}"
        return f"{self._time_created}, {self._name}"

    def __repr__(self) -> str:
        return f"{self.id}, {self._name}"

    @property
    def name(self) -> str:
        return self._name
