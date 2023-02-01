from typing import List, Union, Optional, TYPE_CHECKING
import datetime
import pandas as pd


def indexes_to_axis(
    indexes: Optional[List[Union[int, str, datetime.datetime]]]
) -> Optional[List[Union[int, str, datetime.datetime]]]:
    try:
        if indexes and type(indexes[0]) is str and not str(indexes[0]).isnumeric():
            return list(map(lambda dt: pd.Timestamp(dt), indexes))
        if indexes and type(indexes[0]) is str and str(indexes[0]).isnumeric():
            return list(map(lambda idx: int(str(idx)), indexes))
        return indexes
    except ValueError as e:
        raise ValueError("Could not parse indexes as either int or dates", e)


if TYPE_CHECKING:
    from .ensemble_model import EnsembleModel
    from webviz_ert.plugins import WebvizErtPluginABC


def load_ensemble(
    parent_page: "WebvizErtPluginABC", ensemble_id: str
) -> "EnsembleModel":
    ensemble = parent_page.get_ensemble(ensemble_id=ensemble_id)
    if ensemble is None:
        ensemble = EnsembleModel(
            ensemble_id=ensemble_id, project_id=parent_page.project_identifier
        )
        parent_page.add_ensemble(ensemble)
    return ensemble


from .data_model import DataType, AxisType
from .observation import Observation
from .realization import Realization
from .response import Response
from .plot_model import (
    PlotModel,
    ResponsePlotModel,
    HistogramPlotModel,
    MultiHistogramPlotModel,
    BoxPlotModel,
    ParallelCoordinatesPlotModel,
    BarChartPlotModel,
)
from .parameter_model import PriorModel, ParametersModel
from .ensemble_model import EnsembleModel
