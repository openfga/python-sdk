"""Response wrapper for execute_api_request."""

import json

from dataclasses import dataclass
from typing import Any


@dataclass
class RawResponse:
    """
    Response from execute_api_request / execute_streamed_api_request.

    The body is automatically parsed as JSON if possible,
    otherwise returned as a string or bytes.
    """

    status: int
    """HTTP status code"""

    headers: dict[str, str]
    """Response headers"""

    body: bytes | str | dict[str, Any] | None = None
    """Response body (dict if JSON, otherwise str or bytes)"""

    def json(self) -> dict[str, Any] | None:
        """
        Return the response body as a parsed JSON dictionary.

        :return: Parsed dict or None
        """
        if isinstance(self.body, dict):
            return self.body
        return None

    def text(self) -> str | None:
        """
        Return the response body as a string.

        :return: Body as string, or None
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
