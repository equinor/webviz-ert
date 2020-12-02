from datetime import datetime


def _convertdate(dstring):
    return datetime.strptime(dstring, "%a, %d %b %Y %H:%M:%S GMT")


def indexes_to_axis(indexes):
    try:
        if indexes and type(indexes[0]) is str:
            return list(map(_convertdate, indexes))
        return indexes
    except ValueError as e:
        raise ValueError("Could not parse indexes as either int or dates", e)


from .observation import Observation
from .realization import Realization
from .response import Response
from .plot_model import (
    PlotModel,
    ResponsePlotModel,
    HistogramPlotModel,
    MultiHistogramPlotModel,
)
from .parameter_model import PriorModel, ParametersModel
from .ensemble_model import EnsembleModel
