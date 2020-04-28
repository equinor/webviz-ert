## ertviz

### Introduction

This repository contains some custom dashboards/containers, which are used as
plugins in [webviz-config](https://github.com/equinor/webviz-config).

### Installation

The easiest way of installing this local package is to run
```bash
pip install .
```

If you want to install test and linting dependencies, you can in addition run
```bash
pip install .[tests]
```

### Linting

You can do automatic linting of your code changes by running
```bash
black --check ertviz # Check code style
pylint ertviz # Check code quality
bandit -r ertviz  # Check Python security best practice
```

### Usage and documentation

For general usage, see the documentation on
[webviz-config](https://github.com/equinor/webviz-config).
