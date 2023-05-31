
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

    chromium_version=$(chromium-browser --version | grep -zoP '\d+\.\d+\.\d+')
    chromedriver_version=$(curl -s https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$chromium_version)
    echo "Downloading chromedriver v$chromedriver_version for chromium-browser v$chromium_version"
    wget -O chromedriver.zip https://chromedriver.storage.googleapis.com/$chromedriver_version/chromedriver_linux64.zip
    unzip chromedriver.zip chromedriver -d ../test-kenv/root/bin

    pip install pytest selenium dash[testing]

    pushd tests/data/spe1_st

    echo "Initiating Ert run for Spe1 with new storage enabled..."
    ert ensemble_experiment --enable-new-storage spe1.ert
    echo "Ert ensemble_experiment run finished"

    # $HOST is set to machine name for f_komodo user's bash shells.
    # Must unset for Dash to use localhost as server name, as Selenium expects.
    unset HOST

    echo "Test for webviz-ert plugins..."
    pytest ../../../ -vs -m spe1

    popd
}
