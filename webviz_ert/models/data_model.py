from enum import Enum


class DataType(str, Enum):
    RESPONSE = "resp"
    PARAMETER = "param"
    ENSEMBLE = "ens"
