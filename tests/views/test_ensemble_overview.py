import dash
import dash_html_components as html
import pandas as pd
from ertviz.plugins._ensemble_overview import EnsembleOverview

def test_ensemble_overview(dash_duo, monkeypatch, mocker, tmpdir):
    app = dash.Dash(__name__)

    plugin = EnsembleOverview(mocker.Mock())
    layout = plugin.layout
    app.layout = layout
    dash_duo.start_server(app)
