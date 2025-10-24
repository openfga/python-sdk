"""Tests to ensure internal modules reference the same constant values.

Covers:
- Version consistency between openfga_sdk.__version__ and SDK_VERSION constant
- RetryParams default values match exported retry constants
- ApiClient (async and sync) user agent constants match USER_AGENT constant
- USER_AGENT embeds the SDK_VERSION
"""

from openfga_sdk import Configuration
from openfga_sdk import __version__ as package_version
from openfga_sdk.api_client import (
    DEFAULT_USER_AGENT as ASYNC_DEFAULT_USER_AGENT,
)
from openfga_sdk.constants import (
    DEFAULT_MAX_RETRY,
    DEFAULT_MIN_WAIT_IN_MS,
    MAX_BACKOFF_TIME_IN_SEC,
    SAMPLE_BASE_DOMAIN,
    SDK_VERSION,
    USER_AGENT,
)
from openfga_sdk.sync.api_client import DEFAULT_USER_AGENT as SYNC_DEFAULT_USER_AGENT


def test_version_constant_matches_package_version():
    assert package_version == SDK_VERSION, (
        "openfga_sdk.__version__ must match SDK_VERSION constant"
    )


def test_retry_params_default_constants_alignment():
    cfg = Configuration(api_url=f"https://api.{SAMPLE_BASE_DOMAIN}")
    assert cfg.retry_params.max_retry == DEFAULT_MAX_RETRY
    assert cfg.retry_params.min_wait_in_ms == DEFAULT_MIN_WAIT_IN_MS
    assert cfg.retry_params.max_wait_in_sec == MAX_BACKOFF_TIME_IN_SEC


def test_api_client_user_agent_constant_matches():
    assert ASYNC_DEFAULT_USER_AGENT == USER_AGENT


def test_sync_api_client_user_agent_constant_matches():
    assert SYNC_DEFAULT_USER_AGENT == USER_AGENT


def test_user_agent_contains_version():
    assert SDK_VERSION in USER_AGENT, (
        "USER_AGENT should embed the SDK version for observability"
    )
