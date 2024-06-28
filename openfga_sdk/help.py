import json
import platform
import sys
from collections import OrderedDict

import opentelemetry.version

from . import __version__ as openfga_sdk_version

try:
    import urllib3

    urllib3_version = urllib3.__version__
except ModuleNotFoundError:
    urllib3_version = ""

try:
    import dateutil

    dateutil_version = dateutil.__version__
except ModuleNotFoundError:
    dateutil_version = ""

try:
    import aiohttp

    aiohttp_version = aiohttp.__version__
except ModuleNotFoundError:
    aiohttp_version = ""

try:
    import opentelemetry

    opentelemetry_version = opentelemetry.version.__version__
except ModuleNotFoundError:
    opentelemetry_version = ""


def info() -> dict[str, dict[str, str]]:
    """
    Generate information for a bug report.
    Based on the requests package help utility module.
    """
    try:
        platform_info = {
            "system": platform.system(),
            "release": platform.release(),
        }
    except OSError:
        platform_info = {"system": "Unknown", "release": "Unknown"}

    implementation = platform.python_implementation()

    if implementation == "CPython":
        implementation_version = platform.python_version()
    elif implementation == "PyPy":
        pypy_version_info = sys.pypy_version_info  # type: ignore[attr-defined]
        implementation_version = (
            f"{pypy_version_info.major}."
            f"{pypy_version_info.minor}."
            f"{pypy_version_info.micro}"
        )
        if pypy_version_info.releaselevel != "final":
            implementation_version = "".join(
                [implementation_version, pypy_version_info.releaselevel]
            )
    else:
        implementation_version = "Unknown"

    return OrderedDict(
        {
            "platform": platform_info,
            "implementation": {
                "name": implementation,
                "version": implementation_version,
            },
            "openfga_sdk": {"version": openfga_sdk_version},
            "dependencies": {
                "urllib3": {"version": urllib3_version},
                "python-dateutil": {"version": dateutil_version},
                "aiohttp": {"version": aiohttp_version},
                "opentelemetry": {"version": opentelemetry_version},
            },
        }
    )


def main() -> None:
    """Pretty-print the bug information as JSON."""
    print(json.dumps(info(), indent=2))


if __name__ == "__main__":
    main()
