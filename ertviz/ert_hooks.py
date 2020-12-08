import subprocess
import shutil
import signal
import sys
import os
import logging
import tempfile
import yaml
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


def create_config(project_identifier, config_file, temp_config):
    with open(config_file, "r") as f:
        config_dict = yaml.safe_load(f)
        for page in config_dict["pages"]:
            for element in page["content"]:
                for key in element:
                    element[key] = {"project_identifier": project_identifier}
    output_str = yaml.dump(config_dict)
    temp_config.write(str.encode(output_str))
    temp_config.seek(0)


class WebvizErtPlugin:
    name = "Webviz-ERT"

    @staticmethod
    def run():
        signal.signal(signal.SIGINT, handle_exit)
        # The entry point of webviz is to call it from command line, and so do we.
        if shutil.which("webviz"):
            with tempfile.NamedTemporaryFile() as temp_config:
                project_identifier = os.getenv("ERT_PROJECT_IDENTIFIER")
                if project_identifier is None:
                    logger.error("Unable to find ERT project!")
                create_config(project_identifier, WEBVIZ_CONFIG, temp_config)
                subprocess.run(
                    ["webviz", "build", temp_config.name, "--theme", "equinor"]
                )
        else:
            logger.error("Failed to find webviz")


@hook_implementation
def register_visualization_plugin(handler):
    handler.add_plugin(WebvizErtPlugin)
