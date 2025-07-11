"""
Python SDK for OpenFGA

API version: 1.x
Website: https://openfga.dev
Documentation: https://openfga.dev/docs
Support: https://openfga.dev/community
License: [Apache-2.0](https://github.com/openfga/python-sdk/blob/main/LICENSE)

NOTE: This file was auto generated by OpenAPI Generator (https://openapi-generator.tech). DO NOT EDIT.
"""

from setuptools import find_packages, setup


NAME = "example1"
VERSION = "0.0.1"
REQUIRES = ["openfga-sdk >= 0.9.5"]

setup(
    name=NAME,
    version=VERSION,
    description="An example of using the OpenFGA Python SDK",
    author="OpenFGA (https://openfga.dev)",
    author_email="community@openfga.dev",
    url="https://github.com/openfga/python-sdk",
    install_requires=REQUIRES,
    python_requires=">=3.10",
    packages=find_packages(exclude=["test", "tests"]),
    include_package_data=True,
    license="Apache-2.0",
)
