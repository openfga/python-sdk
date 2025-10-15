import json
import platform
import sys

from . import __version__ as openfga_sdk_version


def get_urllib3_version() -> str:
    try:
        import urllib3

        return urllib3.__version__
    except ModuleNotFoundError:
        return ""


def get_dateutil_version() -> str:
    try:
        import dateutil  # type: ignore[import-untyped]

        version = dateutil.__version__

        if type(version) is not str:
            try:
                version = str(version)
            except Exception:
                pass

        if type(version) is str:
            return version

    except ModuleNotFoundError:
        pass

    return ""


def get_aiohttp_version() -> str:
    try:
        import aiohttp

        return aiohttp.__version__
    except ModuleNotFoundError:
        return ""


def get_opentelemetry_version() -> str:
    try:
        import opentelemetry.version

        return opentelemetry.version.__version__
    except ModuleNotFoundError:
        return ""


def info() -> dict[str, str | dict[str, str] | dict[str, dict[str, str]]]:
    """
    Generate information for a bug report.
    Based on the requests package help utility module.
    """
    platform_info: dict[str, str] = {"system": "Unknown", "release": "Unknown"}
    implementation_version: str = "Unknown"

    try:
        platform_info["system"] = platform.system()
        platform_info["release"] = platform.release()
    except Exception:
        pass

    implementation: str = platform.python_implementation()

    if implementation == "CPython":
        implementation_version = platform.python_version()

    if implementation == "PyPy":
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

    return {
        "platform": platform_info,
        "implementation": {
            "name": implementation,
            "version": implementation_version,
        },
        "openfga_sdk": {"version": openfga_sdk_version},
        "dependencies": {
            "urllib3": {"version": get_urllib3_version()},
            "python-dateutil": {"version": get_dateutil_version()},
            "aiohttp": {"version": get_aiohttp_version()},
            "opentelemetry": {"version": get_opentelemetry_version()},
        },
    }


def main() -> None:
    """Pretty-print the bug information as JSON."""
    print(json.dumps(info(), indent=2))


if __name__ == "__main__":
    main()
