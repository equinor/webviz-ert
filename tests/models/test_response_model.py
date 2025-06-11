from webviz_ert.models import Response


def test_response_model(mock_data):
    resp_model = Response(
        name="SNAKE_OIL_GPR_DIFF@199",
        ensemble_id="1",
        project_id="",
        ensemble_size=1,
        active_realizations=[0],
        resp_schema={"id": "id", "name": "name"},
    )
    assert resp_model.name == "SNAKE_OIL_GPR_DIFF@199"
    assert len(resp_model.data.columns) == 1
