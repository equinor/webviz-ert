from enum import Enum


class DataType(str, Enum):
    RESPONSE = "resp"
    PARAMETER = "param"
    ENSEMBLE = "ens"


class AxisType(str, Enum):
    INDEX = "index"
    TIMESTAMP = "timestamp"
