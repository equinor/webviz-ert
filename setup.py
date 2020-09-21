from setuptools import setup, find_packages
from setuptools_scm import get_version


setup(
    name="ertviz",
    author="Equinor ASA",
    description="ERTVIZ client library",
    url="https://github.com/Equinor/ertviz",
    packages=find_packages(exclude=["tests"]),
    license="GPL-3.0",
    entry_points={},
    install_requires=[
        "webviz-config>=0.0.40",
        "webviz-subsurface-components",
    ],
    platforms="any",
    version=get_version(relative_to=__file__, write_to="ertviz/__version__.py"),
)
