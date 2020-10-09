import pandas
import plotly.express as px


class PriorModel:
    def __init__(self, function, function_parameter_names, function_parameter_values):
        self.function = function
        self.function_parameter_names = function_parameter_names
        self.function_parameter_values = function_parameter_values


class ParameterRealizationModel:
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.selected = True


class ParametersModel:
    def __init__(self, group, key, prior, realizations):
        self.group = group
        self.key = key
        self.priors = prior
        self._realizations = realizations

    def update_selection(self, selection):
        if selection:
            for real in self._realizations:
                real.selected = real.name in selection
        else:
            for real in self._realizations:
                real.selected = True

    @property
    def realizations(self):
        return [real for real in self._realizations if real.selected]

    @property
    def realization_values(self):
        return [real.value for real in self.realizations]

    @property
    def realization_names(self):
        return [real.name for real in self.realizations]

    @property
    def data_frame(self):
        return pandas.DataFrame(
            {
                self.key: [real.value for real in self.realizations],
            }
        )

    @property
    def plot_ids(self):
        return {plot_idx: real.name for plot_idx, real in enumerate(self.realizations)}

    @property
    def repr(self):
        fig = px.histogram(self.data_frame, marginal="rug")
        fig.update_layout(clickmode="event+select")

        fig.update_layout(uirevision=True)
        return fig
