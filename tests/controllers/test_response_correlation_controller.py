import pandas as pd

from webviz_ert.controllers.response_correlation_controller import (
    sort_dataframe,
)


def test_sort_dataframe():
    one_key = "WOPR"
    other_key = "BGMC"
    data = {}
    data[one_key] = [-0.4, 0.6, 0.2]
    data[other_key] = [0.3, 0.8, -0.1]
    dataframe = pd.DataFrame(data=data)
    index = None
    sorted_dataframe, _ = sort_dataframe(dataframe, index, other_key)
    assert list(sorted_dataframe[other_key]) == sorted(data[other_key])
    assert list(sorted_dataframe[one_key]) == [0.2, -0.4, 0.6]
