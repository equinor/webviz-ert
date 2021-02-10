from ertviz.models import Response


def test_ensemble_model(data_loader):
    resp_model = Response.from_data_loader(
        data_loader,
        ensemble_id=1,
        response_id="SNAKE_OIL_GPR_DIFF",
    )
    assert resp_model.name == "SNAKE_OIL_GPR_DIFF"
    assert len(resp_model.realizations) == 1
