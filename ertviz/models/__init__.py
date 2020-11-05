from datetime import datetime


def _convertdate(dstring):
    return datetime.strptime(dstring, "%Y-%m-%d %H:%M:%S")


def indexes_to_axis(indexes):
    if indexes and ":" in indexes[0]:
        return list(map(_convertdate, indexes))
    return list(map(int, indexes))


from .observation import Observation
from .realization import Realization
from .response import Response
from .plot_model import PlotModel, ResponsePlotModel, HistogramPlotModel
from .parameter_model import PriorModel, ParametersModel
from .ensemble_model import EnsembleModel
