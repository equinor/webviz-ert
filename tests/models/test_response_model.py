from ertviz.data_loader import get_ensemble_url
from ertviz.models import Response


def test_ensemble_model(mock_data):
    resp_model = Response(
        "SNAKE_OIL_GPR_DIFF",
        ensemble_id=1,
        response_id="SNAKE_OIL_GPR_DIFF",
    )
    assert resp_model.name == "SNAKE_OIL_GPR_DIFF"
    assert len(resp_model.realizations) == 1
