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
