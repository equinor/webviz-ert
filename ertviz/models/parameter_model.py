import pandas
import math
import plotly.express as px
import plotly.figure_factory as ff
from ertviz.data_loader import get_schema, get_csv_data


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
    def __init__(self, **kwargs):
        self.group = kwargs["group"]
        self.key = kwargs["key"]
        self.priors = kwargs["prior"]
        self._schema_url = kwargs["schema_url"]
        self._realizations = kwargs.get("realizations")
        self.set_plot_param(hist=kwargs.get("hist", True), kde=kwargs.get("kde", True))
        self._data_df = None

    def set_plot_param(self, hist=True, kde=True):
        self._hist_enabled = hist
        self._kde_enabled = kde

    def data_df(self):
        if self._data_df is None:
            realizations_schema = get_schema(self._schema_url)
            self._data_df = get_csv_data(realizations_schema["alldata_url"]).T
            self._data_df.columns = [
                schema["name"]
                for schema in realizations_schema["parameter_realizations"]
            ]
        return self._data_df

    def update_realizations(self, data_df=None):
        if data_df is None:
            data_df = self.data_df()
        if self._realizations is None:
            self._realizations = [
                ParameterRealizationModel(col, data_df[col].values[0])
                for col in data_df
            ]

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
        bin_count = int(math.ceil(math.sqrt(len(self.data_frame.index))))
        bin_size = float(
            (self.data_frame.max().values - self.data_frame.min().values) / bin_count
        )
        fig = ff.create_distplot(
            [self.realization_values],
            [self.key],
            show_hist=self._hist_enabled,
            show_curve=self._kde_enabled,
            bin_size=bin_size,
        )
        fig.update_layout(clickmode="event+select")

        fig.update_layout(uirevision=True)
        return fig
