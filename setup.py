from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

TESTS_REQUIRE = [
    "mypy",
    "bandit",
    "black",
    "dash[testing]",
    "pylint",
    "pytest-mock",
    "selenium~=3.141",
]

setup(
    name="webviz-ert",
    description="Webviz plugins for ERT",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Equinor",
    packages=find_packages(exclude=["tests"]),
    package_data={"webviz_ert.assets": ["*"]},
    include_package_data=True,
    entry_points={
        "webviz_config_plugins": [
            "ResponseComparison = webviz_ert.plugins:ResponseComparison",
            "ObservationAnalyzer = webviz_ert.plugins:ObservationAnalyzer",
            "ParameterComparison = webviz_ert.plugins:ParameterComparison",
            "ResponseCorrelation = webviz_ert.plugins:ResponseCorrelation",
        ],
        "ert": [
            "webviz_ert = webviz_ert.ert_hooks",
        ],
    },
    install_requires=[
        "dash-bootstrap-components",
        "dash-daq",
        "requests",
        "webviz-config>=0.0.40",
        "webviz-config-equinor",
        "webviz-subsurface-components",
    ],
    tests_require=TESTS_REQUIRE,
    extras_require={"tests": TESTS_REQUIRE},
    setup_requires=["setuptools_scm"],
    use_scm_version=True,
    zip_safe=False,
    classifiers=[
        "Natural Language :: English",
        "Environment :: Web Environment",
        "Framework :: Dash",
        "Framework :: Flask",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
)
