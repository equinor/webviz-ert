from webviz_ert.models import EnsembleModel
import dash
from webviz_ert.plugins import ParameterComparison
from webviz_ert.plugins import ObservationAnalyzer
from webviz_ert.models import load_ensemble


def test_ensemble_model(mock_data):
    ens_model = EnsembleModel(ensemble_id=1, project_id=None)
    assert ens_model.name == "default"
    # Will be same as responses in experiment
    assert len(ens_model.responses) == 4


def test_ensemble_model_parameter_data(mock_data):
    ens_id = 42
    ens_model = EnsembleModel(ensemble_id=ens_id, project_id=None)
    parameters = ens_model.parameters
    assert len(parameters) == 2

    data = parameters["SNAKE_OIL_PARAM:OP1_DIVERGENCE_SCALE"].data_df().values
    assert data.flatten().tolist() == [0.1, 1.1, 2.1]

    data = (
        parameters["SNAKE_OIL_PARAM:BPR_138_PERSISTENCE"].data_df()["a"].values.tolist()
    )
    assert data == [0.01, 1.01, 2.01]


def test_ensemble_caching(mock_data):
    app = dash.Dash(__name__)

    plotter_view = ParameterComparison(app, project_identifier=None)
    ens_model_1 = EnsembleModel(ensemble_id=1, project_id=None)
    assert len(plotter_view.get_ensembles()) == 0

    ensemble = plotter_view.get_ensemble(ensemble_id=1)
    assert ensemble is None

    plotter_view.add_ensemble(ens_model_1)
    load_ensemble(plotter_view, ensemble_id=42)

    plotter_view_ensembles = plotter_view.get_ensembles()

    assert len(plotter_view_ensembles) == 2
    assert [ens_id for ens_id, ens_model in plotter_view_ensembles.items()] == [
        1,
        42,
    ]

    page_obs_analyzer = ObservationAnalyzer(app, project_identifier=None)
    page_obs_analyzer_ensembles = page_obs_analyzer.get_ensembles()
    assert len(page_obs_analyzer_ensembles) == 2
    assert page_obs_analyzer_ensembles == plotter_view_ensembles

    plotter_view.clear_ensembles()
    assert len(page_obs_analyzer_ensembles) == 0
    assert len(plotter_view_ensembles) == 0
