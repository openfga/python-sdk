"""
Builders and utilities for execute_api_request functionality.

This module provides reusable utilities for request building, header management,
and response parsing to reduce code duplication across sync and async clients.
"""

import json
import re
import urllib.parse

from typing import Any

from openfga_sdk.exceptions import FgaValidationException


class ExecuteApiRequestBuilder:
    """
    Builder for API request execution.

    Encapsulates request validation, parameter building, and path construction
    to eliminate duplication and improve maintainability.
    """

    def __init__(
        self,
        *,
        operation_name: str,
        method: str,
        path: str,
        path_params: dict[str, str] | None = None,
        body: dict[str, Any] | list[Any] | str | bytes | None = None,
        query_params: dict[str, str | int | list[str | int]] | None = None,
        headers: dict[str, str] | None = None,
    ):
        """Initialize builder with request parameters."""
        self.operation_name = operation_name
        self.method = method
        self.path = path
        self.path_params = path_params
        self.body = body
        self.query_params = query_params
        self.headers = headers

    def validate(self) -> None:
        """
        Validate all required parameters are present.

        :raises FgaValidationException: If any required parameter is missing
        """
        if not self.operation_name:
            raise FgaValidationException(
                "operation_name is required for execute_api_request"
            )
        if not self.method:
            raise FgaValidationException("method is required for execute_api_request")
        if not self.path:
            raise FgaValidationException("path is required for execute_api_request")

    def build_path(self, configured_store_id: str | None = None) -> str:
        """
        Build and validate final resource path with parameter substitution.

        Automatically substitutes {store_id} with configured store_id if not
        explicitly provided in path_params.

        :param configured_store_id: Store ID from client configuration
        :return: Final resource path with all parameters substituted
        :raises FgaValidationException: If path construction fails
        """
        path = self.path
        params = dict(self.path_params) if self.path_params else {}

        # Auto-substitute store_id if needed
        if "{store_id}" in path and "store_id" not in params:
            if not configured_store_id:
                raise FgaValidationException(
                    "Path contains {store_id} but store_id is not configured. "
                    "Set store_id in ClientConfiguration, use set_store_id(), "
                    "or provide it in path_params."
                )
            params["store_id"] = configured_store_id

        # Replace all params
        result = path
        for key, value in params.items():
            placeholder = f"{{{key}}}"
            if placeholder in result:
                encoded = urllib.parse.quote(str(value), safe="")
                result = result.replace(placeholder, encoded)

        # Validate no unresolved params remain
        if "{" in result and "}" in result:
            match = re.search(r"\{([^}]+)\}", result)
            if match:
                raise FgaValidationException(
                    f"Not all path parameters were provided for path: {path}"
                )
        return result

    def build_query_params_list(self) -> list[tuple[str, str]]:
        """
        Convert query_params dict to list of tuples for the API client.

        Handles:
        - List values (expanded to multiple tuples with same key)
        - None values (filtered out)
        - Type conversion to string

        :return: List of (key, value) tuples for query parameters
        """
        if not self.query_params:
            return []

        result = []
        for key, value in self.query_params.items():
            if value is None:
                continue
            if isinstance(value, list):
                result.extend((key, str(item)) for item in value if item is not None)
            else:
                result.append((key, str(value)))
        return result

    def build_headers(
        self,
        options_headers: dict[str, str] | None = None,
    ) -> dict[str, str]:
        """
        Build final headers with proper precedence and SDK enforcement.

        Header precedence (highest to lowest):
        1. SDK-enforced headers (Content-Type, Accept — always application/json)
        2. Options headers (from method options parameter)
        3. Request headers (from headers parameter)

        :param options_headers: Headers from method options
        :return: Final merged headers with SDK enforcement
        """
        result = dict(self.headers) if self.headers else {}
        if options_headers:
            result.update(options_headers)
        # SDK always enforces these for consistent behavior
        result["Content-Type"] = "application/json"
        result["Accept"] = "application/json"
        return result


class ResponseParser:
    """Parse raw REST responses to appropriate Python types."""

    @staticmethod
    def parse_body(
        data: bytes | str | dict[str, Any] | None,
    ) -> bytes | str | dict[str, Any] | None:
        """
        Parse response body, attempting JSON deserialization.

        Handles:
        - None values (returned as-is)
        - Dict objects (returned as-is)
        - String values (attempts JSON parsing, falls back to string)
        - Bytes values (attempts UTF-8 decode + JSON, falls back gracefully)

        :param data: Raw response data from REST client
        :return: Parsed response (dict if JSON, else original type)
        """
        if data is None:
            return None

        if isinstance(data, dict):
            return data

        if isinstance(data, str):
            try:
                return json.loads(data)
            except (json.JSONDecodeError, ValueError):
                return data

        if isinstance(data, bytes):
            try:
                decoded = data.decode("utf-8")
                try:
                    return json.loads(decoded)
                except (json.JSONDecodeError, ValueError):
                    return decoded
            except UnicodeDecodeError:
                return data

        return data
