from typing import List, Set
from webviz_ert.models import Response, EnsembleModel


def _valid_response_option(response_filters: List[str], response: Response) -> bool:
    if "historical" in response_filters:
        if response.name.split(":")[0][-1] == "H":
            return False

    if "obs" in response_filters:
        return response.has_observations

    return True


def response_options(
    response_filters: List[str],
    ensembles: List[EnsembleModel],
) -> Set:
    response_names = set()

    for ensemble in ensembles:
        for name, response in ensemble.responses.items():
            if name in response_names:
                continue
            if _valid_response_option(response_filters, response):
                response_names.add(name)
    return response_names


def parameter_options(ensembles: List[EnsembleModel], union_keys: bool = True) -> Set:
    params_included: Set[str] = set()
    for ensemble in ensembles:
        if ensemble.parameters:
            parameters = set([parameter for parameter in ensemble.parameters])
            if not params_included:
                params_included = parameters
            elif union_keys:
                params_included = params_included.union(parameters)
            else:
                params_included = params_included.intersection(parameters)
    return params_included
