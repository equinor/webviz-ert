import dash
import ertviz
from ertviz.plugins._ensemble_overview import EnsembleOverview


def test_ensemble_overview(
    data_loader,
    dash_duo,
):
    app = dash.Dash(__name__)

    plugin = EnsembleOverview(app, project_identifier=None)
    layout = plugin.layout
    app.layout = layout
    dash_duo.start_server(app)

    ensemble_elements = dash_duo.find_element(".ert-ensemble-selector-large")

    assert ensemble_elements.tag_name == "div"

    minimize_button = dash_duo.wait_for_element_by_css_selector(
        ".ert-ensemble-selector-view-toggle"
    )
    minimize_button.click()
    ensemble_elements = dash_duo.wait_for_element_by_css_selector(
        ".ert-ensemble-selector-small"
    )
    assert dash_duo.get_logs() == [], "browser console should contain no error"
