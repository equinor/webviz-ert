from webviz_ert.models import Response


def test_response_model(mock_data):
    resp_model = Response(
        "SNAKE_OIL_GPR_DIFF",
        ensemble_id="1",
        response_id="SNAKE_OIL_GPR_DIFF",
        project_id="",
        ensemble_size=1,
        active_realizations=[0],
    )
    assert resp_model.name == "SNAKE_OIL_GPR_DIFF"
    assert len(resp_model.data.columns) == 1
