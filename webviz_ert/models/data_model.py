import sys

if sys.version_info < (3, 11):
    from enum import Enum

    class StrEnum(str, Enum):
        pass

else:
    from enum import StrEnum


class DataType(StrEnum):
    RESPONSE = "resp"
    PARAMETER = "param"
    ENSEMBLE = "ens"


class AxisType(StrEnum):
    INDEX = "index"
    TIMESTAMP = "timestamp"
