import pytest
from requests import HTTPError
import dash
from selenium.webdriver.chrome.options import Options


from tests.data.snake_oil_data import ensembles_response


def pytest_addoption(parser):
    """
    Add some command-line options to pytest, so we can set timeout limits,
    e.g. according to which platform we are running the tests on, Azure or
    on-prem.

    These are used by setup_plugin().
    """
    parser.addoption(
        "--implicit-timeout",
        action="store",
        type=int,
        default=2,
        help="implicit timeout in seconds; default 2 s",
    )
    parser.addoption(
        "--explicit-timeout",
        action="store",
        type=int,
        default=10,
        help="explicit timeout in seconds; default 10 s",
    )


# We want to access the options in conftest.py, not in tests;
# this is one way to make the options available as variables.
IMPLICIT_TIMEOUT, EXPLICIT_TIMEOUT = None, None


def pytest_configure(config):
    global IMPLICIT_TIMEOUT, EXPLICIT_TIMEOUT
    IMPLICIT_TIMEOUT = config.getoption("--implicit-timeout")
    EXPLICIT_TIMEOUT = config.getoption("--explicit-timeout")


def pytest_setup_options():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-setuid-sandbox")
    return options


@pytest.fixture
def mock_data(mocker):
    mocker.patch(
        "webviz_ert.data_loader.get_connection_info",
        side_effect=lambda _: {"baseurl": "http://127.0.0.1:5000", "auth": ""},
    )

    mocker.patch("webviz_ert.data_loader._requests_get", side_effect=_requests_get)
    mocker.patch("webviz_ert.data_loader._requests_post", side_effect=_requests_post)


class _MockResponse:
    def __init__(self, url, data, status_code):
        self.url = url
        self.data = data
        self.status_code = status_code

    def json(self):
        return self.data

    @property
    def text(self):
        return self.data

    @property
    def raw(self):
        return self.data

    @property
    def content(self):
        return self.data

    def raise_for_status(self):
        if self.status_code == 400:
            raise HTTPError(
                "Mocked requests raised HTTPError 400 due to missing data in "
                "test-data set!\n"
                f"{self.url}"
            )


def _requests_get(url, **kwargs):
    if kwargs.get("params") is not None:
        url += "?"
        for param, value in kwargs["params"].items():
            url += f"{param}={value}"
    if url in ensembles_response:
        return _MockResponse(url, ensembles_response[url], 200)
    return _MockResponse(url, {}, 400)


def _requests_post(url, **kwargs):
    if url in ensembles_response:
        return _MockResponse(url, ensembles_response[url], 200)
    return _MockResponse(url, {}, 400)


def select_first(dash_duo, selector):
    options = dash_duo.find_elements(selector + " option")
    if not options:
        raise AssertionError(f"No selection option for selector {selector}")
    text = options[0].text
    options[0].click()
    return text


def select_by_name(dash_duo, selector, name):
    dash_duo.wait_for_contains_text(selector, name)
    options = dash_duo.find_elements(selector + " option")
    if not options:
        raise AssertionError(f"No `option`s under selector {selector}")
    for option in options:
        if option.text == name:
            option.click()
            return name
    raise AssertionError(f"Option {name} not available in {selector}")


def get_options(dash_duo, selector):
    parameter_selector_input = dash_duo.find_element(selector)
    return parameter_selector_input.text.split("\n")


def setup_plugin(
    dash_duo,
    name,
    plugin_class,
    window_size=(630, 2000),
    project_identifier=None,
    beta: bool = False,
):
    app = dash.Dash(name)
    plugin = plugin_class(app, project_identifier=project_identifier, beta=beta)
    app.layout = plugin.layout
    dash_duo.start_server(app)
    dash_duo.driver.set_window_size(*window_size)

    # Change timeout periods to help fix flaky tests.
    # These are changed with the command-line options,
    # --implicit-timeout and --implicit-timeout. For example,
    #     pytest --explicit-timeout=20
    # to double the explicit timeout on the wait_for_* calls.
    # Read more about waits in Selenium:
    # https://selenium-python.readthedocs.io/waits.html
    #
    # Implicit waits:
    dash_duo.driver.implicitly_wait(IMPLICIT_TIMEOUT)

    # Explicit waits:
    dash_duo.wait_timeout = EXPLICIT_TIMEOUT  # Requires dash>=2.9.0

    return plugin


def select_ensemble(dash_duo, plugin, wanted_ensemble_name=None):
    """tries to select, i.e. click, the ensemble given by ensemble_name, and
    clicks the first one if no name is given. It returns the name of the
    selected ensemble."""
    ensemble_selector_id = plugin.uuid("ensemble-multi-selector")
    if not wanted_ensemble_name:
        first_ensemble_name = select_first(dash_duo, "#" + ensemble_selector_id)
        dash_duo.wait_for_contains_text(
            "#" + plugin.uuid("selected-ensemble-dropdown"),
            first_ensemble_name,
        )
        return first_ensemble_name

    options_selector_prefix = f"#{ensemble_selector_id}"
    select_by_name(dash_duo, options_selector_prefix, wanted_ensemble_name)
    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("selected-ensemble-dropdown"),
        wanted_ensemble_name,
    )
    return wanted_ensemble_name


def select_response(dash_duo, plugin, response_name=None, wait_for_plot=True) -> str:
    response_selector_id = f'#{plugin.uuid("parameter-selector-multi-resp")}'
    if response_name is None:
        response_name = select_first(dash_duo, response_selector_id)
    else:
        select_by_name(
            dash_duo,
            response_selector_id,
            response_name,
        )
    if wait_for_plot:
        dash_duo.wait_for_element(f"#{plugin.uuid(response_name)}")
    return response_name


def select_parameter(dash_duo, plugin, parameter_name=None, wait_for_plot=True) -> str:
    parameter_selector_id = f'#{plugin.uuid("parameter-selector-multi-param")}'
    if parameter_name is None:
        parameter_name = select_first(dash_duo, parameter_selector_id)
    else:
        select_by_name(
            dash_duo,
            parameter_selector_id,
            parameter_name,
        )
    if wait_for_plot:
        dash_duo.wait_for_element(f"#{plugin.uuid(parameter_name)}")
    return parameter_name


def verify_key_in_dropdown(dash_duo, selector, key):
    verify_keys_in_dropdown(dash_duo, selector, [key])


def verify_keys_in_dropdown(dash_duo, selector, keys):
    dropdown = dash_duo.find_element(f"#{selector}")
    dropdown.click()
    for key in keys:
        dash_duo.wait_for_contains_text(f"#{selector} div.Select-menu-outer", key)
