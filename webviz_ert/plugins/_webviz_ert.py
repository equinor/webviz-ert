from typing import MutableMapping, Optional
import dash
from webviz_config import WebvizPluginABC
from webviz_ert.models import EnsembleModel


class WebvizErtPluginABC(WebvizPluginABC):
    _ensembles: MutableMapping[str, "EnsembleModel"] = {}

    def __init__(self, app: dash.Dash, project_identifier: str):
        super().__init__()
        self.project_identifier: str = project_identifier

    @classmethod
    def get_ensembles(cls) -> MutableMapping[str, "EnsembleModel"]:
        return cls._ensembles

    @classmethod
    def get_ensemble(cls, ensemble_id: str) -> Optional[EnsembleModel]:
        return cls._ensembles.get(ensemble_id)

    @classmethod
    def add_ensemble(cls, ensemble: "EnsembleModel") -> None:
        if ensemble.id not in cls._ensembles:
            cls._ensembles[ensemble.id] = ensemble

    @classmethod
    def clear_ensembles(cls) -> None:
        cls._ensembles.clear()
