from webviz_ert.plugins import (
    ResponseComparison,
    WebvizErtPluginABC,
)
import dash

from tests.conftest import (
    setup_plugin,
    select_ensemble,
    select_parameter,
    select_response,
)


def test_state_saved(mock_data, dash_duo, tmpdir):
    root_path = tmpdir.strpath
    plugin = setup_plugin(
        dash_duo, __name__, ResponseComparison, project_identifier=root_path
    )

    ens_name = "default"
    resp_name = "SNAKE_OIL_GPR_DIFF"
    param_name = "BPR_138_PERSISTENCE"

    select_ensemble(dash_duo, plugin, ens_name)
    select_response(dash_duo, plugin, resp_name)
    select_parameter(dash_duo, plugin, param_name)

    # Check state has been saved
    plugin_state = plugin.load_state()
    assert plugin_state[f"{plugin._class_name}_selected_ensembles"] == [ens_name]
    assert plugin_state[f"{plugin._class_name}_parameter-selection-store-param"] == [
        param_name
    ]
    assert plugin_state[f"{plugin._class_name}_parameter-selection-store-resp"] == [
        resp_name
    ]
    dash_duo.driver.quit()
    # Manually reset the global state
    WebvizErtPluginABC._state = {}
    # Check plugin state is also reset
    assert plugin.load_state() == {}

    # Check initializing new plugin will load state from disk if state is not set
    app = dash.Dash(__name__)
    new_plugin = ResponseComparison(app, project_identifier=root_path)
    new_plugin_state = new_plugin.load_state()

    assert new_plugin_state == plugin_state
    assert new_plugin_state == plugin.load_state()
