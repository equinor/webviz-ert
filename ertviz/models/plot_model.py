import plotly.graph_objects as go


class PlotModel:
    def __init__(self, x_axis, y_axis, text, name, mode, line, marker, error_y=None):
        self._x_axis = x_axis
        self._y_axis = y_axis
        self._text = text
        self._name = name
        self._mode = mode
        self._line = line
        self._marker = marker
        self._error_y = error_y
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
        if type(self._name) is int:
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
