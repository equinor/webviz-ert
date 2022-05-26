from enum import Enum


class DataType(str, Enum):
    RESPONSE = "reps"
    PARAMETER = "param"
    ENSEMBLE = "ens"
