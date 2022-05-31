[![Build Status](https://github.com/equinor/webviz-ert/workflows/Python/badge.svg)](https://github.com/equinor/webviz-ert/actions?query=workflow%3APython)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

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
# Run simulations in ert - <ert-root-folder>/test-data/local/poly_example/
ert ensemble_smoother --target-case smoother poly.ert

# After simulation has finished, start webviz-ert from the same location with
ert vis

# Alternatively, you might have to supply the config file if you're using the
# classic ert storage solution:
ert vis poly.ert
```
