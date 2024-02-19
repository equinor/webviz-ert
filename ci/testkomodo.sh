
copy_test_files () {
    cp -r $CI_SOURCE_ROOT/tests $CI_TEST_ROOT/tests
}

start_tests () {
    start_integration_test
    test_result=$?
    if [ "$test_result" -gt 0 ];
    then
        exit $test_result
    fi
    pytest -vs -m "not spe1"
}

start_integration_test () {

    chromium_version=$(chromium-browser --version | grep -oP '\d+\.\d+\.\d+\.\d+')
    chromium_minor_version=$(echo $chromium_version | grep -oP '^\d+\.\d+\.\d+')

    # Sometimes the chromium-browser has no matching chromedriver.
    download_url="https://storage.googleapis.com/chrome-for-testing-public/$chromium_version/linux64/chromedriver-linux64.zip"

    driver_version=$chromium_version
    if ! wget --spider "$download_url" 2>/dev/null; then
        # If file not exists fall back to last good version
        googlechromelabs_url='https://googlechromelabs.github.io/chrome-for-testing/latest-patch-versions-per-build.json'
        driver_version=$(curl -s "$googlechromelabs_url" | jq -r .builds.\"$chromium_minor_version\".version)
        download_url="https://storage.googleapis.com/chrome-for-testing-public/$driver_version/linux64/chromedriver-linux64.zip"
    fi

    echo "Downloading chromedriver v$driver_version for chromium-browser v$chromium_version"
    wget -O chromedriver.zip "$download_url"
    unzip -j chromedriver.zip chromedriver-linux64/chromedriver -d ../test-kenv/root/bin

    pip install pytest selenium dash[testing]

    pushd tests/data/spe1_st

    echo "Initiating Ert run for Spe1 with new storage enabled..."
    ert ensemble_experiment spe1.ert
    echo "Ert ensemble_experiment run finished"

    # $HOST is set to machine name for f_komodo user's bash shells.
    # Must unset for Dash to use localhost as server name, as Selenium expects.
    unset HOST

    echo "Test for webviz-ert plugins..."
    pytest ../../../ -vs -m spe1

    popd
}
