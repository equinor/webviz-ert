from webviz_ert.models import EnsembleModel
import dash
from webviz_ert.plugins import EnsembleOverview
from webviz_ert.plugins import ObservationAnalyzer
from webviz_ert.models import load_ensemble


def test_ensemble_model(mock_data):
    ens_model = EnsembleModel(ensemble_id=1, project_id=None)
    assert len(ens_model.children) == 1
    assert ens_model.children[0]._name == "default_smoother_update"
    assert ens_model._name == "default"
    assert len(ens_model.responses) == 1


def test_ensemble_model_labled_parameters(mock_data):
    ens_id = 42
    ens_model = EnsembleModel(ensemble_id=ens_id, project_id=None)
    assert ens_model._name == "default"
    assert len(ens_model.parameters) == 3
    for param_name, parameter in ens_model.parameters.items():
        name, label = (
            param_name.split("::", maxsplit=1)
            if "::" in param_name
            else [param_name, None]
        )
        expected_lables = ens_model._data_loader.get_record_labels(ens_id, name)
        if label is not None:
            assert label in expected_lables


def test_ensemble_model_parameter_data(mock_data):
    ens_id = 42
    ens_model = EnsembleModel(ensemble_id=ens_id, project_id=None)
    parameters = ens_model.parameters
    assert len(parameters) == 3

    # Parameter no lables:
    expected_lables = ens_model._data_loader.get_record_labels(
        ens_id, "test_parameter_1"
    )
    assert expected_lables == []
    data = parameters["test_parameter_1"].data_df().values
    assert data.flatten().tolist() == [0.1, 1.1, 2.1]

    # Parameter with lables:
    expected_lables = ens_model._data_loader.get_record_labels(
        ens_id, "test_parameter_2"
    )
    assert expected_lables == ["a", "b"]
    data = parameters["test_parameter_2::a"].data_df()["a"].values.tolist()
    assert data == [0.01, 1.01, 2.01]
    data = parameters["test_parameter_2::b"].data_df()["b"].values.tolist()
    assert data == [0.02, 1.02, 2.02]


def test_ensemble_caching(mock_data):
    app = dash.Dash(__name__)

    page_ens_overview = EnsembleOverview(app, project_identifier=None)
    ens_model_1 = EnsembleModel(ensemble_id=1, project_id=None)
    assert len(page_ens_overview.get_ensembles()) == 0

    ensemble = page_ens_overview.get_ensemble(ensemble_id=1)
    assert ensemble is None

    page_ens_overview.add_ensemble(ens_model_1)
    load_ensemble(page_ens_overview, ensemble_id=42)

    page_ens_overview_ensembles = page_ens_overview.get_ensembles()

    assert len(page_ens_overview_ensembles) == 2
    assert [ens_id for ens_id, ens_model in page_ens_overview_ensembles.items()] == [
        1,
        42,
    ]

    page_obs_analyzer = ObservationAnalyzer(app, project_identifier=None)
    page_obs_analyzer_ensembles = page_obs_analyzer.get_ensembles()
    assert len(page_obs_analyzer_ensembles) == 2
    assert page_obs_analyzer_ensembles == page_ens_overview_ensembles

    page_ens_overview.clear_ensembles()
    assert len(page_obs_analyzer_ensembles) == 0
    assert len(page_ens_overview_ensembles) == 0
