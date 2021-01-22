def _valid_response_option(response_filters, response):
    if "obs" in response_filters:
        return response.observations
    else:
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
