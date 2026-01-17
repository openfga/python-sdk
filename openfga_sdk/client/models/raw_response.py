"""
Raw response wrapper for raw_request method.

This module provides a simple response wrapper for raw HTTP requests
made through the SDK's raw_request method.
"""

from dataclasses import dataclass
from typing import Any


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

        If the body is already a dict (parsed JSON), returns it directly.
        If the body is a string or bytes, attempts to parse it as JSON.
        Returns None if body is None or cannot be parsed.

        :return: Parsed JSON dictionary or None
        """
        if self.body is None:
            return None

        if isinstance(self.body, dict):
            return self.body

        if isinstance(self.body, str):
            import json

            try:
                return json.loads(self.body)
            except (json.JSONDecodeError, ValueError):
                return None

        if isinstance(self.body, bytes):
            import json

            try:
                return json.loads(self.body.decode("utf-8"))
            except (json.JSONDecodeError, ValueError, UnicodeDecodeError):
                return None

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
            import json

            return json.dumps(self.body)

        return str(self.body)
