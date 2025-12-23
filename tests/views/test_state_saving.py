import dash
import pytest

from tests.conftest import (
    select_ensemble,
    select_parameter,
    select_response,
    setup_plugin,
)
from webviz_ert.plugins import ResponseComparison, WebvizErtPluginABC


@pytest.mark.browser_test
def test_state_saved(mock_data, dash_duo, tmpdir):
    root_path = tmpdir.strpath
    plugin = setup_plugin(
        dash_duo, __name__, ResponseComparison, project_identifier=root_path
    )

    ens_name = "default"
    resp_name = "SNAKE_OIL_GPR_DIFF@199"
    param_name = "BPR_138_PERSISTENCE"

    select_ensemble(dash_duo, plugin, ens_name)
    select_response(dash_duo, plugin, resp_name)
    select_parameter(dash_duo, plugin, param_name)

    # Check state has been saved
    plugin_state = plugin.load_state()
    assert plugin_state[f"{plugin._class_name}"]["ensembles"] == [ens_name]
    assert plugin_state[f"{plugin._class_name}"]["param"] == [param_name]
    assert plugin_state[f"{plugin._class_name}"]["resp"] == [resp_name]

    state_before_quit = plugin_state

    # Simulate application exit by killing the driver
    dash_duo.driver.quit()
    # Manually reset the global state
    WebvizErtPluginABC._state = {}
    # Check plugin state is also reset
    assert plugin.load_state() == {}

    # Check initializing new plugin will load state from disk if state is not set
    app = dash.Dash(__name__)
    new_plugin = ResponseComparison(app, project_identifier=root_path)
    state_after_loading = new_plugin.load_state()

    assert state_after_loading == state_before_quit
