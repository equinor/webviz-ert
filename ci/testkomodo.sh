
copy_test_files () {
    cp -r $CI_SOURCE_ROOT/tests $CI_TEST_ROOT/tests
}

install_package () {
    pip install . --no-deps
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
    # Check for HTTP 404 error
    download_url="https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$chromium_version/linux64/chromedriver-linux64.zip"
    download_status=$((curl --head "$download_url" || true) | grep -oP 'HTTP/.+? 200 OK')

    driver_version=$chromium_version
    if [[ -z "$download_status" ]]; then
        # If 404 error, get last good driver version instead.
        googlechromelabs_url='https://googlechromelabs.github.io/chrome-for-testing/latest-patch-versions-per-build.json'
        driver_version=$(curl -s "$googlechromelabs_url" | jq -r .builds.\"$chromium_minor_version\".version)
        download_url="https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$driver_version/linux64/chromedriver-linux64.zip"
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
