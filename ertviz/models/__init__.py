from datetime import datetime


def _convertdate(dstring):
    return datetime.fromisoformat(dstring)


def indexes_to_axis(indexes):
    try:
        if indexes and type(indexes[0]) is str:
            return list(map(_convertdate, indexes))
        return indexes
    except ValueError as e:
        raise ValueError("Could not parse indexes as either int or dates", e)


def load_ensemble(parent_page, ensemble_id):
    ensemble = parent_page.ensembles.get(
        ensemble_id,
        EnsembleModel(
            ensemble_id=int(ensemble_id), project_id=parent_page.project_identifier
        ),
    )
    parent_page.ensembles[ensemble_id] = ensemble
    return ensemble


from .observation import Observation
from .realization import Realization
from .response import Response
from .plot_model import (
    PlotModel,
    ResponsePlotModel,
    HistogramPlotModel,
    MultiHistogramPlotModel,
    BoxPlotModel,
)
from .parameter_model import PriorModel, ParametersModel
from .ensemble_model import EnsembleModel
