import pytest
from requests import HTTPError
import dash
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium import webdriver

from tests.data.snake_oil_data import ensembles_response


def validate_chromedriver():
    try:
        driver = webdriver.Chrome()
        browser_version = driver.capabilities["browserVersion"]
        chromedriver_version = driver.capabilities["chrome"][
            "chromedriverVersion"
        ].split(" ")[0]
        return browser_version[0:3] == chromedriver_version[0:3]
    except (WebDriverException, TypeError):
        return False


def pytest_addoption(parser):
    parser.addoption(
        "--skip-browser-tests",
        action="store_true",
        default=False,
        help="This option allows skipping tests that depend on chromedriver",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "browser_test: mark test as chromedriver dependent"
    )


def pytest_collection_modifyitems(config, items):
    skip_browser_tests = pytest.mark.skip(
        reason="chromedriver missing in PATH or intentionally skipped"
    )
    valid_chromedriver = validate_chromedriver()
    browser_tests = [item for item in items if "browser_test" in item.keywords]
    if valid_chromedriver and not config.getoption("--skip-browser-tests"):
        return
    for item in browser_tests:
        item.add_marker(skip_browser_tests)


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
    # TODO remove wait?
    wait_a_bit(dash_duo, time_seconds=0.5)
    return text


def select_by_name(dash_duo, selector, name):
    dash_duo.wait_for_contains_text(selector, name)
    options = dash_duo.find_elements(selector + " option")
    if not options:
        raise AssertionError(f"No `option`s under selector {selector}")
    for option in options:
        if option.text == name:
            option.click()
            # TODO remove wait?
            wait_a_bit(dash_duo, time_seconds=0.5)
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
    windowsize = window_size
    dash_duo.driver.set_window_size(*windowsize)
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
            timeout=4,
        )
        return first_ensemble_name

    options_selector_prefix = f"#{ensemble_selector_id}"
    select_by_name(dash_duo, options_selector_prefix, wanted_ensemble_name)
    dash_duo.wait_for_contains_text(
        "#" + plugin.uuid("selected-ensemble-dropdown"),
        wanted_ensemble_name,
        timeout=4,
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


def wait_a_bit(dash_duo, time_seconds=0.1):
    try:
        dash_duo.wait_for_element(".foo-elderberries-baarrrrr", timeout=time_seconds)
    except TimeoutException:
        pass


def verify_key_in_dropdown(dash_duo, selector, key):
    verify_keys_in_dropdown(dash_duo, selector, [key])


def verify_keys_in_dropdown(dash_duo, selector, keys):
    dropdown = dash_duo.find_element(f"#{selector}")
    dropdown.click()
    for key in keys:
        dash_duo.wait_for_contains_text(f"#{selector} div.Select-menu-outer", key)
