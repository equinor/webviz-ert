from typing import MutableMapping, TYPE_CHECKING
import dash
from webviz_config import WebvizPluginABC

if TYPE_CHECKING:
    from webviz_ert.models import EnsembleModel, ParametersModel


class WebvizErtPluginABC(WebvizPluginABC):
    def __init__(self, app: dash.Dash, project_identifier: str):
        super().__init__()
        self.project_identifier = project_identifier
        self.ensembles: MutableMapping[int, "EnsembleModel"] = {}
        self.parameter_models: MutableMapping[str, "ParametersModel"] = {}
