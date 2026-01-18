"""
Raw response wrapper for raw_request method.

This module provides a simple response wrapper for raw HTTP requests
made through the SDK's raw_request method.
"""

from dataclasses import dataclass
from typing import Any
import json


@dataclass
class RawResponse:
    """
    Response wrapper for raw HTTP requests.

    This class provides a simple interface to access the response
    from a raw_request call, including status code, headers, and body.

    The body is automatically parsed as JSON if possible, otherwise
    it's returned as a string or bytes.
    """

    status: int
    """HTTP status code"""

    headers: dict[str, str]
    """Response headers as a dictionary"""

    body: bytes | str | dict[str, Any] | None = None
    """Response body (already parsed as dict if JSON, otherwise str or bytes)"""

    def json(self) -> dict[str, Any] | None:
        """
        Return the response body as a JSON dictionary.

        The body is already parsed during the request, so this typically
        just returns the body if it's a dict, or None otherwise.

        :return: Parsed JSON dictionary or None
        """
        if isinstance(self.body, dict):
            return self.body
        return None

    def text(self) -> str | None:
        """
        Return the response body as a string.

        :return: Response body as string or None
        """
        if self.body is None:
            return None

        if isinstance(self.body, str):
            return self.body

        if isinstance(self.body, bytes):
            try:
                return self.body.decode("utf-8")
            except UnicodeDecodeError:
                return self.body.decode("utf-8", errors="replace")

        if isinstance(self.body, dict):
            return json.dumps(self.body)

        return str(self.body)
