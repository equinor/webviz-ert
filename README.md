[![PyPI version](https://badge.fury.io/py/webviz-ert.svg)](https://badge.fury.io/py/webviz-ert)
[![Build Status](https://github.com/equinor/webviz-ert/workflows/Python/badge.svg)](https://github.com/equinor/webviz-ert/actions?query=workflow%3APython)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI license](https://img.shields.io/pypi/l/webviz-ert.svg)](https://pypi.org/project/webviz-ert/)

# Web based visualization for ERT

## What is Webviz-ert
Webviz-ert is a visualization tool for ERT based on [dash](https://github.com/plotly/dash) 
and [webviz-config](https://github.com/equinor/webviz-config).

## Download project
The code is hosted on GitHub:
https://github.com/equinor/webviz-ert

```sh
# From the downloaded project's root folder - to install
pip install .
```

## Running tests
Make sure that you have a browser and driver available for running the tests,
e.g. chrome / chromium and the chrome driver, which should be installed /
downloaded as binaries and made available in the path.

```sh
# From the downloaded project's root folder - to run tests
pip install -r test_requirements.txt
cd tests
pytest
```

## Run Webviz-ert
Webviz-ert connects automatically to a storage server running in [ERT](https://github.com/equinor/ert).
Here are a few steps to get an example version of webviz-ert running.

```sh
# Run simulations in ert - <ert-root-folder>/test-data/ert/poly_example/
ert ensemble_smoother --target-ensemble smoother_%d poly.ert

# After simulation has finished, start webviz-ert from the same location with
ert vis poly.ert
```

## Example

#### Start up 

![startup](https://user-images.githubusercontent.com/4508053/186850915-4b53c4fb-273d-4c15-961c-299966c3232c.gif)

#### Plot viewer 

![plot_viewer](https://user-images.githubusercontent.com/4508053/186850936-38a13f16-f795-4691-8455-fc12f8372d8e.gif)

#### Observation Analyzer

![observation_analyzer](https://user-images.githubusercontent.com/4508053/186850964-68b137eb-17c4-4bf9-9436-81c8c86e5956.gif)

#### Parameter comparison 

![parameter_comparison](https://user-images.githubusercontent.com/4508053/186851000-e5b750e1-d7ae-4da4-a612-b6c3740f5698.gif)

#### Response correlation 

![response_correlation](https://user-images.githubusercontent.com/4508053/186851026-df2085fd-5c35-42a6-a87e-c1890a963254.gif)
