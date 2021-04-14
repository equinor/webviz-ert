import pkg_resources
import json
from pathlib import Path
from webviz_config.webviz_assets import WEBVIZ_ASSETS


ASSETS_DIR = Path(pkg_resources.resource_filename("webviz_ert", "assets"))
WEBVIZ_ASSETS.add(ASSETS_DIR / "bootstrap-grid.css")
WEBVIZ_ASSETS.add(ASSETS_DIR / "ert-style.css")
with open(ASSETS_DIR / "ert-style.json") as f:
    ERTSTYLE = json.load(f)

WEBVIZ_CONFIG = (
    Path(pkg_resources.resource_filename("webviz_ert", "assets")) / "webviz-config.yml"
)
