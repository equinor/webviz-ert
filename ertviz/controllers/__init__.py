import re


def parse_url_query(search):
    return {key: value for (key, value) in re.findall("(\w*)\=(\w*)", search)}


from .response_controller import response_controller
from .parameter_controller import parameter_controller
from .link_and_brush_controller import link_and_brush_controller
from .ensemble_selector_controller import ensemble_selector_controller
