import dateutil.parser
from ertviz.data_loader import data_loader


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
)
from .parameter_model import PriorModel, ParametersModel
from .ensemble import Ensemble


from typing import List
from pydantic import BaseModel


class SimpleEnsemble(BaseModel):
    id: int
    name: str


def list_ensembles(parent_page=None) -> List[SimpleEnsemble]:
    dl = data_loader(parent_page.project_identifier if parent_page else None)
    ensembles = dl.json("/ensembles")
    return [SimpleEnsemble(**ens) for ens in ensembles]


def load_ensemble(parent_page, ensemble_id):
    if ensemble_id not in parent_page.ensembles:
        parent_page.ensembles[ensemble_id] = Ensemble.from_data_loader(
            data_loader=data_loader(parent_page.project_identifier),
            ensemble_id=int(ensemble_id),
        )
    return parent_page.ensembles[ensemble_id]
