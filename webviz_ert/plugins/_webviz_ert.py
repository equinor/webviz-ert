import json
import pathlib
import tempfile
from typing import Any, MutableMapping, Optional

import dash
from webviz_config import WebvizPluginABC

from webviz_ert.models import EnsembleModel


class WebvizErtPluginABC(WebvizPluginABC):
    _ensembles: MutableMapping[str, "EnsembleModel"] = {}
    _state: MutableMapping[str, Any] = {}
    _state_file_name: str = "webviz_ert_state.json"
    _state_path: Optional[pathlib.Path] = None

    def __init__(self, app: dash.Dash, project_identifier: str):
        super().__init__()
        if not project_identifier:
            project_identifier = tempfile.NamedTemporaryFile().name  # noqa: SIM115
            WebvizErtPluginABC._state = {}
            WebvizErtPluginABC._state_path = None

        self.project_identifier: str = project_identifier
        WebvizErtPluginABC._state = self.init_state(pathlib.Path(project_identifier))
        self._class_name: str = type(self).__name__.lower()

    @staticmethod
    def init_state(project_root: pathlib.Path) -> MutableMapping[str, Any]:
        if not WebvizErtPluginABC._state:
            if WebvizErtPluginABC._state_path is None:
                WebvizErtPluginABC._state_path = (
                    project_root / f"{WebvizErtPluginABC._state_file_name}"
                )
            if not WebvizErtPluginABC._state_path.exists():
                WebvizErtPluginABC._state_path.parent.mkdir(parents=True, exist_ok=True)
                return {}
            with open(WebvizErtPluginABC._state_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return WebvizErtPluginABC._state

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

    def save_state(self, key: str, data: Any) -> None:
        page_state = WebvizErtPluginABC._state.get(self._class_name, {})
        page_state[key] = data
        WebvizErtPluginABC._state[self._class_name] = page_state
        if WebvizErtPluginABC._state_path is not None:
            with open(WebvizErtPluginABC._state_path, "w", encoding="utf-8") as f:
                json.dump(WebvizErtPluginABC._state, f, indent=4, sort_keys=True)

    def load_state(
        self, key: Optional[str] = None, default: Optional[Any] = None
    ) -> MutableMapping[str, Any]:
        if key is not None:
            page_state = WebvizErtPluginABC._state.get(self._class_name, {})
            return page_state.get(key, default)

        return WebvizErtPluginABC._state
