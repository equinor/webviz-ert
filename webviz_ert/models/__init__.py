import datetime
from typing import TYPE_CHECKING, List, Optional, Union

import pandas as pd


def indexes_to_axis(
    indexes: Optional[List[Union[int, str, datetime.datetime]]],
) -> Optional[List[Union[int, str, datetime.datetime]]]:
    try:
        if indexes and type(indexes[0]) is str and not str(indexes[0]).isnumeric():
            return [pd.Timestamp(dt) for dt in indexes]
        if indexes and type(indexes[0]) is str and str(indexes[0]).isnumeric():
            return [int(str(idx)) for idx in indexes]
        return indexes
    except ValueError as e:
        raise ValueError("Could not parse indexes as either int or dates", e) from e


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


from .data_model import AxisType as AxisType
from .data_model import DataType as DataType
from .observation import Observation as Observation
from .realization import Realization as Realization
from .response import Response as Response

from .plot_model import (
    BarChartPlotModel as BarChartPlotModel,
)
from .plot_model import (
    BoxPlotModel as BoxPlotModel,
)
from .plot_model import (
    HistogramPlotModel as HistogramPlotModel,
)
from .plot_model import (
    MultiHistogramPlotModel as MultiHistogramPlotModel,
)
from .plot_model import (
    ParallelCoordinatesPlotModel as ParallelCoordinatesPlotModel,
)
from .plot_model import (
    PlotModel as PlotModel,
)
from .plot_model import (
    ResponsePlotModel as ResponsePlotModel,
)

from .parameter_model import ParametersModel as ParametersModel
from .parameter_model import PriorModel as PriorModel
from .ensemble_model import EnsembleModel
