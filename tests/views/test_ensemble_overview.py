import dash

import ertviz
from ertviz.plugins._ensemble_overview import EnsembleOverview
from tests.data.snake_oil_data import ensembles_response


def test_ensemble_overview(dash_duo, monkeypatch, mocker):
    app = dash.Dash(__name__)

    mock_data = ensembles_response["http://127.0.0.1:5000/ensembles"]["ensembles"]

    monkeypatch.setattr(
        ertviz.plugins._ensemble_overview,
        "get_ensembles",
        mocker.Mock(return_value=mock_data),
    )

    plugin = EnsembleOverview(mocker.Mock())
    layout = plugin.layout
    app.layout = layout
    dash_duo.start_server(app)

    ensemble_elements = dash_duo.find_elements("a")
    assert ensemble_elements[0].text == "default"
    assert ensemble_elements[1].text == "default_smoother_update"
    assert dash_duo.get_logs() == [], "browser console should contain no error"
