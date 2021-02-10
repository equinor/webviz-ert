def _valid_response_option(response_filters, response):
    if "obs" in response_filters:
        if response.observations is None or len(response.observations) == 0:
            return False

    if "historical" in response_filters:
        if response.name.split(":")[0][-1] == "H":
            return False

    return True


def response_options(response_filters, ensembles):
    options = []
    for ensemble in ensembles:
        for response in ensemble.responses:
            if (
                _valid_response_option(response_filters, ensemble.responses[response])
                and {"label": response, "value": response} not in options
            ):
                options.append({"label": response, "value": response})
    return options


def parameter_options(ensembles, union_keys=True):
    params_included = None
    for ensemble in ensembles:
        parameters = set([parameter for parameter in ensemble.parameters])
        if params_included is None:
            params_included = parameters
        elif union_keys:
            params_included = params_included.union(parameters)
        else:
            params_included = params_included.intersection(parameters)
    return [{"label": parameter, "value": parameter} for parameter in params_included]
