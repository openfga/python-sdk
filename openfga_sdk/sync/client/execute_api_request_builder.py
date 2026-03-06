"""Re-export for sync client."""

from openfga_sdk.client.execute_api_request_builder import (
    ExecuteApiRequestBuilder,
    ResponseParser,
)


__all__ = [
    "ExecuteApiRequestBuilder",
    "ResponseParser",
]
