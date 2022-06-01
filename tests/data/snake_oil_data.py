import io
import json
import pandas as pd


class DataContent:
    def __init__(self, content):
        self._content = content.encode()

    @property
    def content(self):
        return self._content


all_ensemble_names = [
    "default",
    "default3",
    "default_smoother_update",
    "nr_42",
]

ensembles_response = {
    "http://127.0.0.1:5000/updates/facade": "OK",
    "http://127.0.0.1:5000/experiments": [
        {
            "name": "default",
            "id": 1,
            "ensemble_ids": [1, 2, 3, 42],
            "priors": {
                "BPR_138_PERSISTENCE": {
                    "function": "UNIFORM",
                    "parameter_names": ["MIN", "MAX"],
                    "parameter_values": [0.2, 0.7],
                },
                "OP1_DIVERGENCE_SCALE": {
                    "function": "UNIFORM",
                    "parameter_names": ["MIN", "MAX"],
                    "parameter_values": [0.2, 0.7],
                },
            },
            "userdata": {},
        }
    ],
    "http://127.0.0.1:5000/experiments/1": {
        "name": "default",
        "id": 1,
        "ensemble_ids": [1, 2, 3, 42],
        "priors": {
            "BPR_138_PERSISTENCE": {
                "function": "UNIFORM",
                "parameter_names": ["MIN", "MAX"],
                "parameter_values": [0.2, 0.7],
            },
            "OP1_DIVERGENCE_SCALE": {
                "function": "UNIFORM",
                "parameter_names": ["MIN", "MAX"],
                "parameter_values": [0.2, 0.7],
            },
        },
        "userdata": {},
    },
    "http://127.0.0.1:5000/ensembles/1": {
        "child_ensemble_ids": [2],
        "experiment_id": 1,
        "parent_ensemble_id": None,
        "id": 1,
        "size": 1,
        "active_realizations": [0],
        "userdata": {"name": "default"},
    },
    "http://127.0.0.1:5000/ensembles/1/parameters": [
        {"name": "BPR_138_PERSISTENCE", "labels": []},
        {"name": "OP1_DIVERGENCE_SCALE", "labels": []},
    ],
    "http://127.0.0.1:5000/ensembles/1/responses": {
        "SNAKE_OIL_GPR_DIFF": {
            "name": "SNAKE_OIL_GPR_DIFF",
            "id": "SNAKE_OIL_GPR_DIFF",
            "has_observations": False,
        },
    },
    "http://127.0.0.1:5000/ensembles/2": {
        "experiment_id": 1,
        "child_ensemble_ids": [],
        "parent_ensemble_id": 1,
        "id": 2,
        "size": 1,
        "active_realizations": [0],
        "userdata": {"name": "default_smoother_update"},
    },
    "http://127.0.0.1:5000/ensembles/2/parameters": [
        {"name": "test_parameter_1", "labels": []},
        {"name": "test_parameter_11", "labels": []},
        {"name": "BPR_138_PERSISTENCE", "labels": []},
    ],
    "http://127.0.0.1:5000/ensembles/2/responses": {
        "SNAKE_OIL_GPR_DIFF": {
            "name": "SNAKE_OIL_GPR_DIFF",
            "id": "SNAKE_OIL_GPR_DIFF",
        },
    },
    "http://127.0.0.1:5000/ensembles/3": {
        "experiment_id": 1,
        "child_ensemble_ids": [],
        "name": "default3",
        "parent_ensemble_id": None,
        "id": 3,
        "size": 1,
        "active_realizations": [0],
        "userdata": {"name": "default3"},
    },
    "http://127.0.0.1:5000/ensembles/3/responses": {
        "SNAKE_OIL_GPR_DIFF": {
            "name": "SNAKE_OIL_GPR_DIFF",
            "id": "SNAKE_OIL_GPR_DIFF",
            "has_observations": False,
        },
        "FOPR": {
            "name": "FOPR",
            "id": "FOPR",
            "has_observations": True,
        },
        "WOPR:OP1": {
            "name": "WOPR:OP1",
            "id": "WOPR:OP1",
            "has_observations": True,
        },
    },
    "http://127.0.0.1:5000/ensembles/4": {
        "experiment_id": 1,
        "child_ensemble_ids": [],
        "parent_ensemble_id": None,
        "id": 4,
        "size": 1,
        "active_realizations": [0],
        "userdata": {"name": "default4"},
    },
    "http://127.0.0.1:5000/ensembles/4/responses": {
        "SNAKE_OIL_GPR_DIFF": {
            "name": "SNAKE_OIL_GPR_DIFF",
            "id": "SNAKE_OIL_GPR_DIFF",
        },
        "FOPR": {
            "name": "FOPR",
            "id": "FOPR",
            "has_observations": True,
        },
    },
    "http://127.0.0.1:5000/ensembles/1/records/OP1_DIVERGENCE_SCALE/labels": [],
    "http://127.0.0.1:5000/ensembles/1/records/BPR_138_PERSISTENCE/labels": [],
    "http://127.0.0.1:5000/ensembles/1/records/SNAKE_OIL_GPR_DIFF/observations?realization_index=0": [],
    "http://127.0.0.1:5000/ensembles/3/records/SNAKE_OIL_GPR_DIFF?realization_index=0": pd.DataFrame(
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        columns=[0],
        index=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    )
    .transpose()
    .to_csv()
    .encode(),
    "http://127.0.0.1:5000/ensembles/3/records/SNAKE_OIL_GPR_DIFF/observations?realization_index=0": [],
    "http://127.0.0.1:5000/ensembles/3/responses/FOPR?realization_index=0": pd.DataFrame(
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        columns=[0],
        index=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    )
    .transpose()
    .to_csv()
    .encode(),
    "http://127.0.0.1:5000/ensembles/3/records/FOPR/observations?realization_index=0": [],
    "http://127.0.0.1:5000/ensembles/3/records/WOPR:OP1?realization_index=0": pd.DataFrame(
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        columns=[0],
        index=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    )
    .transpose()
    .to_csv()
    .encode(),
    "http://127.0.0.1:5000/ensembles/3/records/WOPR:OP1/observations?realization_index=0": [
        {
            "x_axis": {"data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]},
            "errors": {"data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]},
            "values": {"data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]},
            "name": "WOPR:OP1",
        }
    ],
    "http://127.0.0.1:5000/ensembles/4/records/SNAKE_OIL_GPR_DIFF?realization_index=0": pd.DataFrame(
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        columns=[0],
        index=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    )
    .transpose()
    .to_csv()
    .encode(),
    "http://127.0.0.1:5000/ensembles/4/records/SNAKE_OIL_GPR_DIFF/observations?realization_index=0": [],
    "http://127.0.0.1:5000/ensembles/4/responses/FOPR?realization_index=0": pd.DataFrame(
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        columns=[0],
        index=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    )
    .transpose()
    .to_csv()
    .encode(),
    "http://127.0.0.1:5000/ensembles/4/records/FOPR/observations?realization_index=0": [
        {
            "x_axis": {"data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]},
            "errors": {"data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]},
            "values": {"data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]},
            "name": "FOPR",
        }
    ],
}


def to_parquet_helper(dataframe: pd.DataFrame) -> bytes:
    stream = io.BytesIO()
    dataframe.to_parquet(stream)
    return stream.getvalue()


ensembles_response[
    "http://127.0.0.1:5000/ensembles/1/records/SNAKE_OIL_GPR_DIFF?realization_index=0"
] = to_parquet_helper(
    pd.DataFrame(
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        columns=["0"],
        index=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
    ).transpose()
)

ensembles_response[
    "http://127.0.0.1:5000/ensembles/1/records/SNAKE_OIL_GPR_DIFF"
] = to_parquet_helper(
    pd.DataFrame(
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        columns=["0"],
        index=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
    ).transpose()
)

ensembles_response[
    "http://127.0.0.1:5000/ensembles/1/records/OP1_DIVERGENCE_SCALE"
] = to_parquet_helper(
    pd.DataFrame(
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        columns=["0"],
        index=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
    ).transpose()
)


ensembles_response[
    "http://127.0.0.1:5000/ensembles/1/records/BPR_138_PERSISTENCE"
] = to_parquet_helper(
    pd.DataFrame(
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        columns=["0"],
        index=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
    ).transpose()
)

ensembles_response.update(
    {
        "http://127.0.0.1:5000/ensembles/42": {
            "child_ensemble_ids": [],
            "experiment_id": 1,
            "parent_ensemble_id": None,
            "id": 42,
            "name": "nr_42",
            "size": 1,
            "active_realizations": [0],
            "userdata": {"name": "nr_42"},
        },
        "http://127.0.0.1:5000/ensembles/42/parameters": [
            {"name": "test_parameter_1", "labels": []},
            {"name": "test_parameter_2", "labels": ["a", "b"]},
            {"name": "test_parameter_77", "labels": []},
            {"name": "test_parameter_11", "labels": []},
        ],
        "http://127.0.0.1:5000/ensembles/42/responses": {
            "test_response": {
                "name": "name_test_response",
                "id": "test_response_id_1",
            },
            "test_response_99": {
                "name": "name_test_response",
                "id": "test_response_id_99",
            },
            "test_response_44": {
                "name": "name_test_response",
                "id": "test_response_id_44",
            },
            "test_response_4": {
                "name": "name_test_response",
                "id": "test_response_id_4",
            },
        },
        "http://127.0.0.1:5000/ensembles/42/records/test_parameter_1/labels": [],
        "http://127.0.0.1:5000/ensembles/42/records/test_parameter_2/labels": [
            "a",
            "b",
        ],
        "http://127.0.0.1:5000/ensembles/42/records/test_parameter_77/labels": [],
        "http://127.0.0.1:5000/ensembles/42/records/test_parameter_11/labels": [],
    }
)

ensembles_response[
    "" "http://127.0.0.1:5000/ensembles/42/records/test_parameter_1?"
] = to_parquet_helper(
    pd.DataFrame(
        [0.1, 1.1, 2.1],
        columns=["0"],
        index=["0", "1", "2"],
    ).transpose()
)
ensembles_response[
    "http://127.0.0.1:5000/ensembles/42/records/test_parameter_2?label=a"
] = to_parquet_helper(
    pd.DataFrame(
        [0.01, 1.01, 2.01],
        columns=["a"],
        index=["0", "1", "2"],
    ).transpose()
)
ensembles_response[
    "http://127.0.0.1:5000/ensembles/42/records/test_parameter_2?label=b"
] = to_parquet_helper(
    pd.DataFrame(
        [0.02, 1.02, 2.02],
        columns=["b"],
        index=["0", "1", "2"],
    ).transpose()
)
