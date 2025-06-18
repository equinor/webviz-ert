import io
import pandas as pd

from webviz_ert.data_loader import escape


class DataContent:
    def __init__(self, content):
        self._content = content.encode()

    @property
    def content(self):
        return self._content


def to_parquet_helper(dataframe: pd.DataFrame) -> bytes:
    stream = io.BytesIO()
    dataframe.to_parquet(stream)
    return stream.getvalue()


all_ensemble_names = [
    "default",
    "default3",
    "default_smoother_update",
    "nr_42",
]

_experiment_1_metadata = {
    "name": "default",
    "id": 1,
    "ensemble_ids": [1, 2, 3, 42],
    "priors": {
        "SNAKE_OIL_PARAM:BPR_138_PERSISTENCE": {
            "function": "UNIFORM",
            "parameter_names": ["MIN", "MAX"],
            "parameter_values": [0.2, 0.7],
        },
        "SNAKE_OIL_PARAM:OP1_DIVERGENCE_SCALE": {
            "function": "UNIFORM",
            "parameter_names": ["MIN", "MAX"],
            "parameter_values": [0.2, 0.7],
        },
    },
    "parameters": {
        "SNAKE_OIL_PARAM": [
            {
                "key": "SNAKE_OIL_PARAM:OP1_DIVERGENCE_SCALE",
                "transformation": "UNIFORM",
                "dimensionality": 1,
                "userdata": {"data_origin": "GEN_KW"},
            },
            {
                "key": "SNAKE_OIL_PARAM:BPR_138_PERSISTENCE",
                "transformation": "UNIFORM",
                "dimensionality": 1,
                "userdata": {"data_origin": "GEN_KW"},
            },
        ]
    },
    "responses": {
        "summary": [
            {"response_type": "summary", "response_key": "FGPT", "filter_on": None},
            {"response_type": "summary", "response_key": "WOPR:OP1", "filter_on": None},
            {"response_type": "summary", "response_key": "FOPR", "filter_on": None},
        ],
        "gen_data": [
            {
                "response_type": "gen_data",
                "response_key": "SNAKE_OIL_GPR_DIFF",
                "filter_on": {"report_step": [199]},
            }
        ],
    },
    "observations": {
        "summary": {
            "FOPR": ["FOPR"],
            "WOPR:OP1": [
                "WOPR_OP1_108",
                "WOPR_OP1_9",
                "WOPR_OP1_144",
                "WOPR_OP1_190",
                "WOPR_OP1_36",
                "WOPR_OP1_72",
            ],
        }
    },
    "userdata": {},
}

ensembles_response = {
    "http://127.0.0.1:5000/updates/facade": "OK",
    "http://127.0.0.1:5000/experiments": [
        _experiment_1_metadata,
    ],
    "http://127.0.0.1:5000/experiments/1": _experiment_1_metadata,
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
        "FGPT": {
            "name": "FGPT",
            "id": "FGPT",
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
    "http://127.0.0.1:5000/ensembles/3/parameters": [
        {"name": "BPR_138_PERSISTENCE", "labels": []},
        {"name": "OP1_DIVERGENCE_SCALE", "labels": []},
    ],
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
    "http://127.0.0.1:5000/ensembles/1/responses/SNAKE_OIL_GPR_DIFF/observations?realization_index=0": [],
    "http://127.0.0.1:5000/ensembles/3/responses/SNAKE_OIL_GPR_DIFF?realization_index=0": pd.DataFrame(
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        columns=[0],
        index=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    )
    .transpose()
    .to_csv()
    .encode(),
    "http://127.0.0.1:5000/ensembles/3/responses/SNAKE_OIL_GPR_DIFF/observations?realization_index=0": [],
    "http://127.0.0.1:5000/ensembles/3/responses/FOPR/observations?realization_index=0": [
        {
            "x_axis": ["2010-01-10 00:00:00", "2010-04-10 00:00:00"],
            "errors": [4, 2],
            "values": [0.42, 0.24],
            "name": "FOPR",
        }
    ],
    "http://127.0.0.1:5000/ensembles/3/responses/FOPR": to_parquet_helper(
        pd.DataFrame(
            [0.24, 0.13, 0.22, 0.36, 0.21, 0.54, 0.12, 0.16, 0.23, 0.18],
            index=[
                "2010-01-10 00:00:00",
                "2010-02-10 00:00:00",
                "2010-03-10 00:00:00",
                "2010-04-10 00:00:00",
                "2010-05-10 00:00:00",
                "2010-06-10 00:00:00",
                "2010-07-10 00:00:00",
                "2010-08-10 00:00:00",
                "2010-09-10 00:00:00",
                "2010-10-10 00:00:00",
            ],
            columns=[0],
        ).transpose()
    ),
    "http://127.0.0.1:5000/ensembles/3/responses/FGPT/observations?realization_index=0": [],
    "http://127.0.0.1:5000/ensembles/3/responses/FGPT": to_parquet_helper(
        pd.DataFrame(
            [0.1, 1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 7.1, 8.1, 9.1],
            columns=[0],
            index=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
        ).transpose()
    ),
    "http://127.0.0.1:5000/ensembles/3/responses/WOPR%253AOP1": to_parquet_helper(
        pd.DataFrame(
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            columns=[0],
            index=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
        ).transpose()
    ),
    "http://127.0.0.1:5000/ensembles/3/responses/WOPR%253AOP1/observations?realization_index=0": [
        {
            "x_axis": [1, 4],
            "errors": [1, 1],
            "values": [1, 5],
            "name": "WOPR:OP1",
        }
    ],
    "http://127.0.0.1:5000/ensembles/4/responses/SNAKE_OIL_GPR_DIFF?realization_index=0": pd.DataFrame(
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        columns=[0],
        index=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    )
    .transpose()
    .to_csv()
    .encode(),
    "http://127.0.0.1:5000/ensembles/4/responses/SNAKE_OIL_GPR_DIFF/observations?realization_index=0": [],
    "http://127.0.0.1:5000/ensembles/4/responses/FOPR?realization_index=0": pd.DataFrame(
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        columns=[0],
        index=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    )
    .transpose()
    .to_csv()
    .encode(),
    "http://127.0.0.1:5000/ensembles/4/responses/FOPR/observations?realization_index=0": [
        {
            "x_axis": {"data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]},
            "errors": {"data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]},
            "values": {"data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]},
            "name": "FOPR",
        }
    ],
}


ensembles_response[
    "http://127.0.0.1:5000/ensembles/1/responses/SNAKE_OIL_GPR_DIFF?realization_index=0"
] = to_parquet_helper(
    pd.DataFrame(
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        columns=["0"],
        index=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
    ).transpose()
)

ensembles_response[
    'http://127.0.0.1:5000/ensembles/1/responses/SNAKE_OIL_GPR_DIFF?filter_on={"report_step": "199"}'
] = to_parquet_helper(
    pd.DataFrame(
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        columns=["0"],
        index=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
    ).transpose()
)

ensembles_response[
    "http://127.0.0.1:5000/ensembles/1/parameters/OP1_DIVERGENCE_SCALE"
] = to_parquet_helper(
    pd.DataFrame(
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        columns=["0"],
        index=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
    ).transpose()
)


ensembles_response[
    "http://127.0.0.1:5000/ensembles/1/parameters/BPR_138_PERSISTENCE"
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
            [
                {"name": "SNAKE_OIL_PARAM:OP1_DIVERGENCE_SCALE", "labels": []},
                {"name": "SNAKE_OIL_PARAM:BPR_138_PERSISTENCE", "labels": []},
            ]
        ],
        "http://127.0.0.1:5000/ensembles/42/responses": {
            "SNAKE_OIL_PARAM:OP1_DIVERGENCE_SCALE": {
                "name": "SNAKE_OIL_PARAM:BPR_138_PERSISTENCE",
                "id": "SNAKE_OIL_PARAM:OP1_DIVERGENCE_SCALE",
            },
            "SNAKE_OIL_PARAM:BPR_138_PERSISTENCE": {
                "name": "SNAKE_OIL_PARAM:BPR_138_PERSISTENCE",
                "id": "SNAKE_OIL_PARAM:BPR_138_PERSISTENCE",
            },
        },
    }
)


ensembles_response[
    f"http://127.0.0.1:5000/ensembles/42/parameters/{escape('SNAKE_OIL_PARAM:OP1_DIVERGENCE_SCALE')}?"
] = to_parquet_helper(
    pd.DataFrame(
        [0.1, 1.1, 2.1],
        columns=["0"],
        index=["0", "1", "2"],
    ).transpose()
)
ensembles_response[
    f"http://127.0.0.1:5000/ensembles/42/parameters/{escape('SNAKE_OIL_PARAM:BPR_138_PERSISTENCE')}?"
] = to_parquet_helper(
    pd.DataFrame(
        [0.01, 1.01, 2.01],
        columns=["a"],
        index=["0", "1", "2"],
    ).transpose()
)
