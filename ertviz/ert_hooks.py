import subprocess
import shutil
import signal
import sys
import os
import logging
from ert_shared.plugins.plugin_manager import hook_implementation
from ertviz.assets import WEBVIZ_CONFIG


logger = logging.getLogger()


def handle_exit(*args):  # pylint: disable=unused-argument)
    logger.info("\n" + "=" * 32)
    logger.info("Session terminated by the user.\n" "Thank you for using webviz-ert!")
    logger.info("=" * 32)
    sys.tracebacklimit = 0
    sys.stdout = open(os.devnull, "w")
    sys.exit()


class WebvizErtPlugin:
    name = "Webviz-ERT"

    @staticmethod
    def run():
        signal.signal(signal.SIGINT, handle_exit)
        # The entry point of webviz is to call it from command line, and so do we.
        if shutil.which("webviz"):
            subprocess.run(["webviz", "build", WEBVIZ_CONFIG, "--theme", "equinor"])
        else:
            logger.error("Failed to find webviz")


@hook_implementation
def register_visualization_plugin(handler):
    handler.add_plugin(WebvizErtPlugin)
