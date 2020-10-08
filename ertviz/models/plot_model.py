class PlotModel:
    def __init__(self, x_axis, y_axis, text, name, mode, line, marker):
        self._x_axis = x_axis
        self._y_axis = y_axis
        self._text = text
        self._name = name
        self._mode = mode
        self._line = line
        self._marker = marker

    @property
    def repr(self):
        repr_dict = dict(
            x=self._x_axis,
            y=self._y_axis,
            text=self._text,
            name=self._name,
            mode=self._mode,
        )
        if self._line:
            repr_dict["line"] = self._line
        if self._marker:
            repr_dict["marker"] = self._marker

        return repr_dict


class EnsemblePlotModel:
    def __init__(self, realization_plots, observations, layout):
        self._realization_plots = realization_plots
        self._observations = observations
        self._layout = layout

    @property
    def repr(self):
        return dict(
            data=[rel.repr for rel in self._realization_plots]
            + [obs.repr for obs in self._observations],
            layout=self._layout,
        )
