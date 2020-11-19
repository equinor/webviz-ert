class DataContent:
    def __init__(self, content):
        self._content = content.encode()

    @property
    def content(self):
        return self._content


ensembles_response = {
    "http://127.0.0.1:5000/ensembles": {
        "ensembles": [
            {
                "children": [
                    {
                        "name": "default_smoother_update",
                        "ref_url": "http://127.0.0.1:5000/ensembles/2",
                    }
                ],
                "name": "default",
                "parent": {},
                "ref_url": "http://127.0.0.1:5000/ensembles/1",
                "time_created": "2020-04-29T09:36:26",
            },
            {
                "children": [],
                "name": "default_smoother_update",
                "parent": {
                    "name": "default",
                    "ref_url": "http://127.0.0.1:5000/ensembles/1",
                },
                "ref_url": "http://127.0.0.1:5000/ensembles/2",
                "time_created": "2020-04-29T09:43:25",
            },
        ]
    },
    "http://127.0.0.1:5000/ensembles/1": {
        "children": [
            {
                "name": "default_smoother_update",
                "ref_url": "http://127.0.0.1:5000/ensembles/2",
            }
        ],
        "name": "default",
        "parameters": [
            {
                "group": "SNAKE_OIL_PARAM",
                "key": "BPR_138_PERSISTENCE",
                "prior": {
                    "function": "UNIFORM",
                    "parameter_names": ["MIN", "MAX"],
                    "parameter_values": [0.2, 0.7],
                },
                "ref_url": "http://127.0.0.1:5000/ensembles/1/parameters/1",
            },
        ],
        "parent": {},
        "realizations": [
            {"name": 0, "ref_url": "http://127.0.0.1:5000/ensembles/1/realizations/0"},
            {"name": 1, "ref_url": "http://127.0.0.1:5000/ensembles/1/realizations/1"},
            {"name": 2, "ref_url": "http://127.0.0.1:5000/ensembles/1/realizations/2"},
        ],
        "ref_url": "http://127.0.0.1:5000/ensembles/1",
        "responses": [
            {
                "name": "SNAKE_OIL_GPR_DIFF",
                "ref_url": "http://127.0.0.1:5000/ensembles/1/responses/SNAKE_OIL_GPR_DIFF",
            },
        ],
        "time_created": "2020-04-29T09:36:26",
    },
    "http://127.0.0.1:5000/ensembles/2": {
        "children": [],
        "name": "default_smoother_update",
        "parameters": [
            {
                "group": "SNAKE_OIL_PARAM",
                "key": "BPR_138_PERSISTENCE",
                "prior": {
                    "function": "UNIFORM",
                    "parameter_names": ["MIN", "MAX"],
                    "parameter_values": [0.2, 0.7],
                },
                "ref_url": "http://127.0.0.1:5000/ensembles/1/parameters/1",
            },
        ],
        "parent": {
            "name": "default",
            "ref_url": "http://127.0.0.1:5000/ensembles/1",
        },
        "realizations": [
            {"name": 0, "ref_url": "http://127.0.0.1:5000/ensembles/1/realizations/0"},
            {"name": 1, "ref_url": "http://127.0.0.1:5000/ensembles/1/realizations/1"},
            {"name": 2, "ref_url": "http://127.0.0.1:5000/ensembles/1/realizations/2"},
        ],
        "ref_url": "http://127.0.0.1:5000/ensembles/2",
        "responses": [
            {
                "name": "SNAKE_OIL_GPR_DIFF",
                "ref_url": "http://127.0.0.1:5000/ensembles/1/responses/SNAKE_OIL_GPR_DIFF",
            },
        ],
        "time_created": "2020-04-29T10:36:26",
    },
    "http://127.0.0.1:5000/ensembles/1/parameters/1": {
        "alldata_url": "http://127.0.0.1:5000/ensembles/1/parameters/1/data",
        "group": "SNAKE_OIL_PARAM",
        "key": "BPR_138_PERSISTENCE",
        "parameter_realizations": [
            {
                "data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                "name": 0,
                "realization": {
                    "ref_url": "http://127.0.0.1:5000/ensembles/1/realizations/0"
                },
            },
            {
                "data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                "name": 1,
                "realization": {
                    "ref_url": "http://127.0.0.1:5000/ensembles/1/realizations/1"
                },
            },
            {
                "data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                "name": 2,
                "realization": {
                    "ref_url": "http://127.0.0.1:5000/ensembles/1/realizations/2"
                },
            },
        ],
        "prior": {
            "function": "UNIFORM",
            "parameter_names": ["MIN", "MAX"],
            "parameter_values": [0.2, 0.7],
        },
        "ref_url": "http://127.0.0.1:5000/ensembles/1/parameters/1",
    },
    "http://127.0.0.1:5000/ensembles/1/realizations/0": {
        "name": 0,
        "parameters": [
            {
                "data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                "name": "BPR_138_PERSISTENCE",
            },
            {
                "data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                "name": "BPR_555_PERSISTENCE",
            },
            {
                "data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                "name": "OP1_DIVERGENCE_SCALE",
            },
        ],
        "responses": [
            {
                "data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                "name": "SNAKE_OIL_GPR_DIFF",
            },
            {
                "data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                "name": "SNAKE_OIL_OPR_DIFF",
            },
            {
                "data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                "name": "SNAKE_OIL_WPR_DIFF",
            },
        ],
    },
    "http://127.0.0.1:5000/ensembles/1/responses/SNAKE_OIL_GPR_DIFF": {
        "alldata_url": "http://127.0.0.1:5000/ensembles/1/responses/SNAKE_OIL_GPR_DIFF/data",
        "axis": {"data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]},
        "ensemble_id": "1",
        "name": "SNAKE_OIL_GPR_DIFF",
        "realizations": [
            {
                "data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                "name": 0,
                "ref_url": "http://127.0.0.1:5000/ensembles/1/realizations/0",
                "summarized_misfits": {},
                "univariate_misfits": {},
            }
        ],
    },
    "http://127.0.0.1:5000/ensembles/1/responses/FOPR": {
        "alldata_url": "http://127.0.0.1:5000/ensembles/1/responses/FOPR/data",
        "axis": {"data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]},
        "ensemble_id": "1",
        "name": "FOPR",
        "observations": [
            {
                "data": {
                    "data_indexes": {"data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]},
                    "key_indexes": {"data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]},
                    "std": {"data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]},
                    "values": {"data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]},
                },
                "name": "FOPR",
            }
        ],
        "realizations": [
            {
                "data": "http://127.0.0.1:5000/data/726",
                "name": 0,
                "ref_url": "http://127.0.0.1:5000/ensembles/1/realizations/0",
                "summarized_misfits": {"FOPR": 946.263115564503},
                "univariate_misfits": {
                    "FOPR": [
                        {"obs_index": 0, "sign": True, "value": 1.3776484533744848},
                        {"obs_index": 1, "sign": True, "value": 1.384794184010784},
                        {"obs_index": 2, "sign": True, "value": 1.3966335691013885},
                    ]
                },
            }
        ],
    },
    "http://127.0.0.1:5000/ensembles/1/parameters/1/data": 0.1,
}
