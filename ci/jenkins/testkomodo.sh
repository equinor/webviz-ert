
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
    pytest -vs -k "not spe1"
}

start_integration_test () {
    
    echo "Downloading chromedriver ..."
    wget -O chromedriver.zip https://chromedriver.storage.googleapis.com/90.0.4430.24/chromedriver_linux64.zip
    unzip chromedriver.zip chromedriver -d ../test-kenv/root/bin

    pip install pytest selenium dash[testing]

    pushd tests/data/spe1_st

    echo "Initiating Ert run for Spe1 with new storage enabled..."

    ert ensemble_experiment --enable-new-storage spe1.ert

    echo "Ert ensemble_esmeble experiment run finished"

    echo "Run the storage server api ..."
    ert api &
    ert_api_pid=$!
    max_sec=30
    until [ -f storage_server.json ]
    do
        if [ "$max_sec" -le 0 ]
        then
            echo "ert-storage has not started properly!"
            exit 1
        fi
        sleep 1
        max_sec=$(( max_sec-1 ))
    done

    echo "Test for webviz-ert plugins ..."
    popd
    set +e
    pytest -vs -k spe1
    status=$?
    echo "Close the storage server api ... "
    kill $ert_api_pid
    wait $ert_api_pid
    echo "Completed"
    return "$status"
}
