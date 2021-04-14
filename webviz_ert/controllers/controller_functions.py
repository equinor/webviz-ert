from typing import List, Dict, Optional, Set
from webviz_ert.models import Response, EnsembleModel


def _valid_response_option(response_filters: List[str], response: Response) -> bool:
    if "obs" in response_filters:
        if response.observations is None or len(response.observations) == 0:
            return False

    if "historical" in response_filters:
        if response.name.split(":")[0][-1] == "H":
            return False

    return True


def response_options(
    response_filters: List[str], ensembles: List[EnsembleModel]
) -> List[Dict]:
    options = []
    for ensemble in ensembles:
        for response in ensemble.responses:
            if (
                _valid_response_option(response_filters, ensemble.responses[response])
                and {"label": response, "value": response} not in options
            ):
                options.append({"label": response, "value": response})
    return options


def parameter_options(
    ensembles: List[EnsembleModel], union_keys: bool = True
) -> List[Dict]:
    params_included: Optional[Set[str]] = None
    for ensemble in ensembles:
        if ensemble.parameters:
            parameters = set([parameter for parameter in ensemble.parameters])
            if not params_included:
                params_included = parameters
            elif union_keys:
                params_included = params_included.union(parameters)
            else:
                params_included = params_included.intersection(parameters)
    if params_included:
        return [
            {"label": parameter, "value": parameter} for parameter in params_included
        ]
    return []
