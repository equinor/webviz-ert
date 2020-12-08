import dash
import ertviz
from ertviz.plugins._ensemble_overview import EnsembleOverview
from tests.data.snake_oil_data import ensembles_response


def test_ensemble_overview(dash_duo, monkeypatch, mocker):
    app = dash.Dash(__name__)

    plugin = EnsembleOverview(mocker.Mock(), project_identifier=None)
    layout = plugin.layout
    app.layout = layout
    dash_duo.start_server(app)

    ensemble_elements = dash_duo.find_element(".ert-ensemble-selector")

    assert ensemble_elements.tag_name == "div"
    assert dash_duo.get_logs() == [], "browser console should contain no error"
