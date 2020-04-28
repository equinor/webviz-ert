## ertviz

### Introduction

This repository contains some custom dashboards/containers, which are used as
plugins in [webviz-config](https://github.com/equinor/webviz-config).

(The history of) this repository will be wiped/removed, after some quick/dirty initial prototyping.

### Installation

As this uses non-published `ert` functionality and `ertviz` functionality
you will need to run some command lines in order to get a working environment:

```bash
# Create a new virtual environment
source /prog/res/komodo/testing-py3/enable
python -m venv ertviz_venv --system-site-packages
source ertviz_venv/bin/activate

# Install the ert API feature branch
git clone git@github.com:equinor/ert.git
pushd ert
git fetch origin ertviz
git checkout ertviz
pip install -e .
popd

# Install this ertviz repository
pip install --upgrade webviz-config
git clone git@github.com:equinor/ertviz
pushd ertviz
pip install -e .
popd

export no_proxy="localhost,127.0.0.1"
```

Before starting `ertviz` plugins, you will currently also need to manually first start the ERT API server with some existing data:
```
cd ./ert/test-data/local/snake_oil
ert api
```
