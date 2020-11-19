import re


def parse_url_query(search):
    return {key: value for (key, value) in re.findall("(\w*)\=(\w*)", search)}


from .link_and_brush_controller import link_and_brush_controller
from .ensemble_selector_controller import ensemble_selector_controller
from .multi_response_controller import multi_response_controller
from .observation_response_controller import observation_response_controller
from .multi_parameter_controller import multi_parameter_controller
