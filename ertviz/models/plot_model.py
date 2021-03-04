import math
import pandas as pd
import logging
import plotly.graph_objects as go
import plotly.figure_factory as ff
from scipy.stats import norm, lognorm, truncnorm, uniform, loguniform, triang
import ertviz.assets as assets

"""
Unsupported priors
CONST
DUNIF
ERRF
DERRF
"""

logger = logging.getLogger()

WARNING_MSG = """Plotting {prior_type} is not yet fully supported.
Please contact us on slack channel #ert-users if this is a desired feature."""


def _TRIANGULAR(xaxis, xmin, xmode, xmax):
    loc = xmin
    scale = xmax - xmin
    c = (xmode - xmin) / scale
    return triang.pdf(xaxis, c, loc, scale)


def _TRUNC_NORMAL(xaxis, mean, std, _min, _max):
    logger.warning(WARNING_MSG.format(prior_type="TRUNCATED_NORMAL"))
    a = (_min - mean) / std
    b = (_max - mean) / std
    return truncnorm.pdf(xaxis, a, b, mean, std)


def _CONST(xaxis, value):
    logger.warning(WARNING_MSG.format(prior_type="CONST"))
    return [value for x in xaxis]


def _UNIFORM(xaxis, _min, _max):
    loc = _min
    scale = _max - _min
    return uniform.pdf(xaxis, loc, scale)


def _DUNIFORM(xaxis, _steps, _min, _max):
    logger.warning(WARNING_MSG.format(prior_type="DUNIF"))
    loc = _min
    scale = _max - _min
    return uniform.pdf(xaxis, loc, scale)


def _RAW(xaxis):
    return norm.pdf(xaxis, 0, 1)


def _ERRF(*args):
    logger.warning(WARNING_MSG.format(prior_type="ERRF"))
    return []


def _DERRF(*args):
    logger.warning(WARNING_MSG.format(prior_type="DERRF"))
    return []


PRIOR_FUNCTIONS = {
    "NORMAL": norm.pdf,
    "LOGNORMAL": lognorm.pdf,
    "TRUNCATED_NORMAL": _TRUNC_NORMAL,
    "UNIFORM": _UNIFORM,
    "DUNIF": _DUNIFORM,
    "LOGUNIF": loguniform.pdf,
    "TRIANGULAR": _TRIANGULAR,
    "CONST": _CONST,
    "RAW": _RAW,
    "ERRF": _ERRF,
    "DERRF": _DERRF,
}


def _create_prior_plot(name, prior, _min, _max, color):
    n = 100
    diff = (_max - _min) / n
    xaxis = [_min + i * diff for i in range(n)]
    yaxis = PRIOR_FUNCTIONS[prior.function](xaxis, *prior.function_parameter_values)
    style = assets.ERTSTYLE["parameter-plot"]["prior"].copy()
    style["line"]["color"] = color

    return go.Scattergl(name=f"{name}-prior", x=xaxis, y=yaxis, line=style["line"])


class BoxPlotModel:
    def __init__(self, **kwargs):
        self.selected = True
        self._y_axis = kwargs["y_axis"]
        self._name = kwargs["name"]
        self._color = kwargs["color"]

    @property
    def repr(self):
        repr_dict = dict(
            y=self._y_axis,
            name=self.display_name,
            boxpoints="all",
            jitter=0.3,
            pointpos=-1.8,
            marker_color=self._color,
        )

        return go.Box(repr_dict)

    @property
    def name(self):
        return self._name

    @property
    def display_name(self):
        if isinstance(self._name, int):
            return f"Value {self._name}"
        else:
            return self._name


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
            text=self._text,
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
    def __init__(
        self,
        data_df_dict,
        names,
        colors,
        hist=True,
        kde=True,
        priors={},
        bin_count=None,
    ):
        self._hist_enabled = hist
        self._kde_enabled = kde
        self._data_df_dict = data_df_dict
        self.selection = []
        self._colors = colors
        self._priors = priors
        self._bin_count = bin_count
        self._names = names

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
    def bin_count(self):
        if self._bin_count is None:
            # get any dict response data_frame, so the first is a good choice
            data = list(self._data_df_dict.values())[0].values.flatten()
            self._bin_count = int(math.ceil(math.sqrt(len(data)))) - 1
        return self._bin_count

    @property
    def repr(self):
        colors = []
        data = []
        names = []
        realization_nums = []
        for name in self._data_df_dict:
            data.append(list(self._data_df_dict[name].values.flatten()))
            colors.append(self._colors[name])
            names.append(self._names[name])
            realization_nums.append(
                [f"Realization {num}" for num in self._data_df_dict[name].columns]
            )

        _max = max(map(max, data))
        _min = min(map(min, data))
        bin_size = float((_max - _min) / self.bin_count)
        fig = ff.create_distplot(
            data,
            names,
            show_hist=self._hist_enabled,
            show_curve=self._kde_enabled,
            bin_size=bin_size,
            colors=colors,
            show_rug=True,
            rug_text=realization_nums,
            curve_type="normal",
            histnorm="probability density",
        )
        for name, (prior, color) in self._priors.items():
            fig.add_trace(_create_prior_plot(name, prior, _min, _max, color))
        fig.update_layout(clickmode="event+select")
        fig.update_layout(assets.ERTSTYLE["figure"]["layout"])
        return fig


class ParallelCoordinatesPlotModel:
    def __init__(self, data_df_dict, colors):
        self._data_df_dict = data_df_dict
        self._colors = colors
        self.selection = []

    @property
    def plot_ids(self):
        return {plot_idx: parameter for plot_idx, parameter in enumerate(self.data)}

    @property
    def data(self):
        return self._data_df_dict

    @property
    def repr(self):
        fig = go.Figure()
        # rearange colors
        colors = []
        for idx, ens in enumerate(self._colors):
            colors.append([idx / len(self._colors), self._colors[ens]])
            colors.append([(idx + 1) / len(self._colors), self._colors[ens]])
        # create a single dataframe, where all ensemble parameters are stacked
        data_df = pd.concat(list(self.data.values()))
        # drop a column with ids
        ensemble_ids = data_df["ensemble_id"]
        data_df = data_df.drop("ensemble_id", axis=1)
        # create parallel coordinates dimension list
        dimensions = []
        for parameter in data_df:
            dimensions.append(dict(label=parameter, values=data_df[parameter]))
        fig.add_trace(
            go.Parcoords(
                line=dict(
                    color=ensemble_ids,
                    colorscale=colors,
                    showscale=True,
                    colorbar=dict(
                        tickvals=list(range(0, len(self.data))),
                        ticktext=list(self.data.keys()),
                        len=0.2 * len(self.data),
                        title="Ensemble",
                    ),
                ),
                dimensions=dimensions,
                labelangle=45,
                labelside="top",
            )
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

        fig.update_layout(assets.ERTSTYLE["figure"]["layout"])
        return fig
