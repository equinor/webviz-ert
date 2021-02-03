from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

TESTS_REQUIRE = [
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
    package_data={"ertviz.assets": ["*"]},
    include_package_data=True,
    entry_points={
        "webviz_config_plugins": [
            "EnsembleOverview = ertviz.plugins:EnsembleOverview",
            "ResponseComparison = ertviz.plugins:ResponseComparison",
            "ObservationAnalyzer = ertviz.plugins:ObservationAnalyzer",
            "ParameterComparison = ertviz.plugins:ParameterComparison",
        ],
        "ert": [
            "ertviz = ertviz.ert_hooks",
        ],
    },
    install_requires=[
        "dash-cytoscape",
        "dash-bootstrap-components",
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
