import warnings

with warnings.catch_warnings():
    warnings.filterwarnings(
        "ignore",
        message=r".*pkg_resources is deprecated as an API.*",
        category=UserWarning,
    )
    import pkg_resources
import json
from pathlib import Path
from webviz_config.webviz_assets import WEBVIZ_ASSETS


ASSETS_DIR = Path(pkg_resources.resource_filename("webviz_ert", "assets"))
WEBVIZ_ASSETS.add(ASSETS_DIR / "bootstrap-grid.css")
WEBVIZ_ASSETS.add(ASSETS_DIR / "bootstrap.min.css")
WEBVIZ_ASSETS.add(ASSETS_DIR / "ert-style.css")
with open(ASSETS_DIR / "ert-style.json") as f:
    ERTSTYLE = json.load(f)

COLOR_WHEEL = ERTSTYLE["ensemble-selector"]["color_wheel"]

WEBVIZ_CONFIG = (
    Path(pkg_resources.resource_filename("webviz_ert", "assets")) / "webviz-config.yml"
)


def get_color(index: int) -> str:
    return COLOR_WHEEL[index % len(COLOR_WHEEL)]
