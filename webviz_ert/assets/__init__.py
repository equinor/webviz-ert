import json
import sys

if sys.version_info >= (3, 9):
    from importlib.resources import files
else:
    from importlib_resources import files
from webviz_config.webviz_assets import WEBVIZ_ASSETS

ASSETS_DIR = files("webviz_ert") / "assets"
WEBVIZ_ASSETS.add(ASSETS_DIR / "bootstrap-grid.css")
WEBVIZ_ASSETS.add(ASSETS_DIR / "bootstrap.min.css")
WEBVIZ_ASSETS.add(ASSETS_DIR / "ert-style.css")
with open(ASSETS_DIR / "ert-style.json", encoding="utf-8") as f:
    ERTSTYLE = json.load(f)

COLOR_WHEEL = ERTSTYLE["ensemble-selector"]["color_wheel"]

WEBVIZ_CONFIG = files("webviz_ert") / "assets" / "webviz-config.yml"


def get_color(index: int) -> str:
    return COLOR_WHEEL[index % len(COLOR_WHEEL)]
