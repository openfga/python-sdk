"""
Python SDK for OpenFGA

API version: 1.x
Website: https://openfga.dev
Documentation: https://openfga.dev/docs
Support: https://openfga.dev/community
License: [Apache-2.0](https://github.com/openfga/python-sdk/blob/main/LICENSE)
"""

from typing import Final


# Version of the OpenFGA Python SDK.
SDK_VERSION: Final[str] = "0.10.4"  # x-release-please-version

# User agent used in HTTP requests.
USER_AGENT: Final[str] = f"openfga-sdk python/{SDK_VERSION}"
