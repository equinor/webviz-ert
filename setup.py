from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    LONG_DESCRIPTION = fh.read()

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
    },
    install_requires=[
        "dash-bootstrap-components",
        "dash-daq",
        "pandas",
        "requests",
        "webviz-config>=0.0.40",
        "webviz-config-equinor",
        "webviz-subsurface-components",
    ],
    setup_requires=["setuptools_scm"],
    use_scm_version=True,
    zip_safe=False,
    classifiers=[
        "Natural Language :: English",
        "Environment :: Web Environment",
        "Framework :: Dash",
        "Framework :: Flask",
        "Topic :: Scientific/Engineering",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
    ],
)
