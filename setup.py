"""
Python SDK for OpenFGA

API version: 1.x
Website: https://openfga.dev
Documentation: https://openfga.dev/docs
Support: https://openfga.dev/community
License: [Apache-2.0](https://github.com/openfga/python-sdk/blob/main/LICENSE)

NOTE: This file was auto generated by OpenAPI Generator (https://openapi-generator.tech). DO NOT EDIT.
"""

import pathlib

import pkg_resources

from setuptools import find_packages, setup


NAME = "openfga-sdk"
VERSION = "0.9.3"
REQUIRES = []


with pathlib.Path("requirements.txt").open() as requirements_txt:
    REQUIRES = [
        str(requirement)
        for requirement in pkg_resources.parse_requirements(requirements_txt)
    ]

this_directory = pathlib.Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name=NAME,
    version=VERSION,
    description="A high performance and flexible authorization/permission engine built for developers and inspired by Google Zanzibar.",
    author="OpenFGA (https://openfga.dev)",
    author_email="community@openfga.dev",
    url="https://github.com/openfga/python-sdk",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords=[
        "openfga",
        "authorization",
        "fga",
        "fine-grained-authorization",
        "rebac",
        "zanzibar",
    ],
    install_requires=REQUIRES,
    python_requires=">=3.10",
    packages=find_packages(exclude=["test"]),
    include_package_data=True,
    license="Apache-2.0",
    long_description_content_type="text/markdown",
    long_description=long_description,
)
