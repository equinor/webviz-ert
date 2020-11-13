import plotly.graph_objects as go
import plotly.figure_factory as ff
import math


class PlotModel:
    def __init__(self, **kwargs):
        self._x_axis = kwargs["x_axis"]
        self._y_axis = kwargs["y_axis"]
        self._text = kwargs["text"]
        self._name = kwargs["name"]
        self._mode = kwargs["mode"]
        self._line = kwargs["line"]
        self._marker = kwargs["marker"]
        self._error_y = kwargs.get("error_y")
        self.selected = True

    @property
    def repr(self):
        repr_dict = dict(
            x=self._x_axis,
            y=self._y_axis,
            text=self.display_name,
            name=self.display_name,
            mode=self._mode,
            error_y=self._error_y,
        )
        if self._line:
            repr_dict["line"] = self._line
        if self._marker:
            repr_dict["marker"] = self._marker
        if self.selected:
            repr_dict["visible"] = True
        else:
            repr_dict["visible"] = "legendonly"
        return go.Scattergl(repr_dict)

    @property
    def name(self):
        return self._name

    @property
    def display_name(self):
        if isinstance(self._name, int):
            return f"Realization {self._name}"
        else:
            return self._name


class ResponsePlotModel:
    def __init__(self, realization_plots, observations, layout):
        self._realization_plots = realization_plots
        self._observations = observations
        self._layout = layout
        self.selection = []

    @property
    def repr(self):
        if self.selection:
            for real in self._realization_plots:
                real.selected = real.name in self.selection
        else:
            for real in self._realization_plots:
                real.selected = True

        fig = go.Figure(layout=self._layout)
        for rel in self._realization_plots:
            fig.add_trace(rel.repr)
        for obs in self._observations:
            fig.add_trace(obs.repr)
        return fig

    @property
    def plot_ids(self):
        return {idx: rel.name for idx, rel in enumerate(self._realization_plots)}


class MultiHistogramPlotModel:
    def __init__(self, data_df_dict, colors, hist=True, kde=True):
        self._hist_enabled = hist
        self._kde_enabled = kde
        self._data_df_dict = data_df_dict
        self.selection = []
        self._colors = colors

    @property
    def data_df(self):
        if self.selection:
            return [
                {response_name: self._data_df_dict[response_name][self.selection]}
                for response_name in self._data_df_dict
            ]
        return self._data_df_dict

    @property
    def plot_ids(self):
        df = self._data_df_dict.values()[0]
        return {plot_idx: real.name for plot_idx, real in enumerate(df)}

    @property
    def repr(self):
        colors = []
        data = []
        names = []
        for response_name in self._data_df_dict:
            data.append(list(self._data_df_dict[response_name].values.flatten()))
            colors.append(self._colors[response_name])
            names.append(response_name)

        bin_count = int(math.ceil(math.sqrt(len(data[0]))))
        _max = max(map(max, data))
        _min = min(map(min, data))
        bin_size = float((_max - _min) / bin_count)
        fig = ff.create_distplot(
            data,
            names,
            show_hist=self._hist_enabled,
            show_curve=self._kde_enabled,
            bin_size=bin_size,
            colors=colors,
        )
        fig.update_layout(clickmode="event+select")

        fig.update_layout(uirevision=True)
        return fig


class HistogramPlotModel:
    def __init__(self, data_df, hist=True, kde=True):
        self._hist_enabled = hist
        self._kde_enabled = kde
        self._data_df = data_df
        self.selection = []

    @property
    def data_df(self):
        if self.selection:
            return self._data_df[self.selection]
        return self._data_df

    @property
    def plot_ids(self):
        return {plot_idx: real.name for plot_idx, real in enumerate(self._data_df)}

    @property
    def repr(self):
        bin_count = int(math.ceil(math.sqrt(len(self.data_df.values.flatten()))))
        bin_size = float(
            (self.data_df.max(axis=1).values - self.data_df.min(axis=1).values)
            / bin_count
        )
        fig = ff.create_distplot(
            [list(self.data_df.values.flatten())],
            [self.data_df.index.name],
            show_hist=self._hist_enabled,
            show_curve=self._kde_enabled,
            bin_size=bin_size,
        )
        fig.update_layout(clickmode="event+select")

        fig.update_layout(uirevision=True)
        return fig
