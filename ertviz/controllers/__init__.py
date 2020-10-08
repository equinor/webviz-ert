import re


def parse_url_query(search):
    return {key: value for (key, value) in re.findall("(\w*)\=(\w*)", search)}


from .response_controller import response_controller
from .parameter_controller import parameter_controller
