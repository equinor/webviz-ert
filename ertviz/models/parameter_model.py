class PriorModel:
    def __init__(self, function, function_parameter_names, function_parameter_values):
        self.function = function
        self.function_parameter_names = function_parameter_names
        self.function_parameter_values = function_parameter_values


class ParameterRealizationModel:
    def __init__(self, name, value):
        self.name = name
        self.value = value


class ParametersModel:
    def __init__(self, group, key, prior, realizations):
        self.group = group
        self.key = key
        self.priors = prior
        self.realizations = realizations

    @property
    def realization_values(self):
        return [real.value for real in self.realizations]

    @property
    def realization_names(self):
        return [real.name for real in self.realizations]
