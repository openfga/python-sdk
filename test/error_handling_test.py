"""
Unit tests for enhanced error handling.

These tests verify that:
1. Error messages are properly formatted
2. Error properties are accessible
3. Helper methods work correctly
"""

import pytest
from openfga_sdk.exceptions import (
    ApiException,
    ValidationException,
    NotFoundException,
    ServiceException,
    RateLimitExceededError,
)
from openfga_sdk.models import ValidationErrorMessageResponse
from openfga_sdk.models.error_code import ErrorCode


class MockHTTPResponse:
    """Mock HTTP response for testing."""

    def __init__(self, status, reason, data, headers=None):
        self.status = status
        self.reason = reason
        self.data = data
        # Create a mock headers object with items() method
        self.headers = MockHeaders(headers or {})

    def getheaders(self):
        return self.headers


class MockHeaders:
    """Mock headers object."""

    def __init__(self, headers_dict):
        self._headers = headers_dict

    def items(self):
        return list(self._headers.items())


class TestEnhancedErrorHandling:
    """Tests for enhanced error handling functionality."""

    def test_error_message_format_with_all_fields(self):
        """Test that error messages include all components when available."""
        # Create a mock response
        response = MockHTTPResponse(
            status=400,
            reason="Bad Request",
            data=b'{"code": "validation_error", "message": "type \'invalid_type\' not found"}',
            headers={"fga-request-id": "test-request-123"}
        )

        # Create exception
        exc = ValidationException(http_resp=response, operation_name="write")

        # Set parsed exception
        parsed = ValidationErrorMessageResponse(
            code=ErrorCode.VALIDATION_ERROR,
            message="type 'invalid_type' not found"
        )
        exc.parsed_exception = parsed

        # Verify string representation
        error_str = str(exc)
        assert "[write]" in error_str
        assert "HTTP 400" in error_str
        assert "type 'invalid_type' not found" in error_str
        assert "(validation_error)" in error_str
        assert "[request-id: test-request-123]" in error_str

    def test_error_properties_accessible(self):
        """Test that all error properties are accessible."""
        response = MockHTTPResponse(
            status=400,
            reason="Bad Request",
            data=b'{}',
            headers={"fga-request-id": "test-request-456"}
        )

        exc = ValidationException(http_resp=response, operation_name="check")
        parsed = ValidationErrorMessageResponse(
            code=ErrorCode.VALIDATION_ERROR,
            message="Invalid relation"
        )
        exc.parsed_exception = parsed

        # Test properties
        assert exc.operation_name == "check"
        assert exc.status == 400
        assert exc.code == "validation_error"
        assert exc.error_message == "Invalid relation"
        assert exc.request_id == "test-request-456"

    def test_is_validation_error_helper(self):
        """Test is_validation_error() helper method."""
        response = MockHTTPResponse(400, "Bad Request", b'{}')
        exc = ValidationException(http_resp=response)
        parsed = ValidationErrorMessageResponse(code=ErrorCode.VALIDATION_ERROR)
        exc.parsed_exception = parsed

        assert exc.is_validation_error() is True
        assert exc.is_client_error() is True
        assert exc.is_server_error() is False
        assert exc.is_retryable() is False

    def test_is_not_found_error_helper(self):
        """Test is_not_found_error() helper method."""
        response = MockHTTPResponse(404, "Not Found", b'{}')
        exc = NotFoundException(http_resp=response)

        assert exc.is_not_found_error() is True
        assert exc.is_client_error() is True
        assert exc.is_server_error() is False
        assert exc.is_retryable() is False

    def test_is_authentication_error_helper(self):
        """Test is_authentication_error() helper method."""
        response = MockHTTPResponse(401, "Unauthorized", b'{}')
        exc = ApiException(http_resp=response)

        assert exc.is_authentication_error() is True
        assert exc.is_client_error() is True

    def test_is_rate_limit_error_helper(self):
        """Test is_rate_limit_error() helper method."""
        response = MockHTTPResponse(429, "Too Many Requests", b'{}')
        exc = RateLimitExceededError(http_resp=response)

        assert exc.is_rate_limit_error() is True
        assert exc.is_retryable() is True
        assert exc.is_client_error() is True

    def test_is_server_error_helper(self):
        """Test is_server_error() helper method."""
        response = MockHTTPResponse(500, "Internal Server Error", b'{}')
        exc = ServiceException(http_resp=response)

        assert exc.is_server_error() is True
        assert exc.is_client_error() is False
        assert exc.is_retryable() is True

    def test_is_retryable_helper(self):
        """Test is_retryable() helper for various status codes."""
        # Retryable errors
        for status in [429, 500, 502, 503, 504]:
            response = MockHTTPResponse(status, "Error", b'{}')
            exc = ApiException(http_resp=response)
            assert exc.is_retryable() is True, f"Status {status} should be retryable"

        # Non-retryable errors
        for status in [400, 401, 403, 404]:
            response = MockHTTPResponse(status, "Error", b'{}')
            exc = ApiException(http_resp=response)
            assert exc.is_retryable() is False, f"Status {status} should not be retryable"

    def test_error_without_parsed_exception(self):
        """Test error handling when parsed_exception is not set."""
        response = MockHTTPResponse(400, "Bad Request", b'{}')
        exc = ValidationException(http_resp=response, operation_name="write")

        # Should use reason as fallback
        assert exc.error_message == "Bad Request"
        assert exc.code is None

        # String representation should still work
        error_str = str(exc)
        assert "[write]" in error_str
        assert "HTTP 400" in error_str
        assert "Bad Request" in error_str

    def test_error_without_operation_name(self):
        """Test error handling when operation_name is not set."""
        response = MockHTTPResponse(400, "Bad Request", b'{}')
        exc = ApiException(http_resp=response)
        parsed = ValidationErrorMessageResponse(
            code=ErrorCode.VALIDATION_ERROR,
            message="Test error"
        )
        exc.parsed_exception = parsed

        # Should not include operation name
        error_str = str(exc)
        assert not error_str.startswith("[")
        assert "HTTP 400" in error_str
        assert "Test error" in error_str

    def test_error_without_request_id(self):
        """Test error handling when request_id is not available."""
        response = MockHTTPResponse(400, "Bad Request", b'{}', headers={})
        exc = ValidationException(http_resp=response, operation_name="write")

        assert exc.request_id is None

        # String representation should not include request-id
        error_str = str(exc)
        assert "[request-id:" not in error_str

    def test_error_code_with_enum(self):
        """Test that error code property handles enum values."""
        response = MockHTTPResponse(400, "Bad Request", b'{}')
        exc = ValidationException(http_resp=response)

        # Create parsed exception with enum
        parsed = ValidationErrorMessageResponse(code=ErrorCode.VALIDATION_ERROR)
        exc.parsed_exception = parsed

        # Should return the enum value as string
        assert exc.code == "validation_error"
        assert isinstance(exc.code, str)

    def test_multiple_errors_have_unique_messages(self):
        """Test that different errors have different details."""
        # Error 1: Invalid type
        response1 = MockHTTPResponse(400, "Bad Request", b'{}')
        exc1 = ValidationException(http_resp=response1, operation_name="write")
        parsed1 = ValidationErrorMessageResponse(
            code=ErrorCode.VALIDATION_ERROR,
            message="type 'invalid_type' not found"
        )
        exc1.parsed_exception = parsed1

        # Error 2: Invalid relation
        response2 = MockHTTPResponse(400, "Bad Request", b'{}')
        exc2 = ValidationException(http_resp=response2, operation_name="write")
        parsed2 = ValidationErrorMessageResponse(
            code=ErrorCode.VALIDATION_ERROR,
            message="relation 'invalid_relation' not found"
        )
        exc2.parsed_exception = parsed2

        # Same code, different messages
        assert exc1.code == exc2.code
        assert exc1.error_message != exc2.error_message
        assert "invalid_type" in exc1.error_message
        assert "invalid_relation" in exc2.error_message

    def test_operation_context_preserved(self):
        """Test that operation name is preserved in exception."""
        response = MockHTTPResponse(400, "Bad Request", b'{}')

        write_exc = ValidationException(http_resp=response, operation_name="write")
        assert write_exc.operation_name == "write"

        check_exc = ValidationException(http_resp=response, operation_name="check")
        assert check_exc.operation_name == "check"

        read_exc = ValidationException(http_resp=response, operation_name="read")
        assert read_exc.operation_name == "read"

    def test_error_message_consistency(self):
        """Test that error message format is consistent."""
        import re

        response = MockHTTPResponse(
            400, "Bad Request", b'{}',
            headers={"fga-request-id": "req-123"}
        )
        exc = ValidationException(http_resp=response, operation_name="write")
        parsed = ValidationErrorMessageResponse(
            code=ErrorCode.VALIDATION_ERROR,
            message="Test error"
        )
        exc.parsed_exception = parsed

        error_str = str(exc)

        # Should match pattern: [operation] HTTP status message (code) [request-id: id]
        pattern = r"^\[write\] HTTP 400 Test error \(validation_error\) \[request-id: req-123\]$"
        assert re.match(pattern, error_str), f"Error string '{error_str}' doesn't match expected pattern"

    def test_client_vs_server_error_categorization(self):
        """Test that client and server errors are properly categorized."""
        # Client errors (4xx)
        for status in [400, 401, 403, 404, 429]:
            response = MockHTTPResponse(status, "Error", b'{}')
            exc = ApiException(http_resp=response)
            assert exc.is_client_error() is True
            assert exc.is_server_error() is False

        # Server errors (5xx)
        for status in [500, 502, 503, 504]:
            response = MockHTTPResponse(status, "Error", b'{}')
            exc = ApiException(http_resp=response)
            assert exc.is_server_error() is True
            assert exc.is_client_error() is False

    def test_exception_subclass_helpers(self):
        """Test that helper methods work for exception subclasses."""
        # ValidationException
        response = MockHTTPResponse(400, "Bad Request", b'{}')
        exc = ValidationException(http_resp=response)
        assert exc.is_validation_error() is True

        # NotFoundException
        response = MockHTTPResponse(404, "Not Found", b'{}')
        exc = NotFoundException(http_resp=response)
        assert exc.is_not_found_error() is True

        # ServiceException
        response = MockHTTPResponse(500, "Internal Server Error", b'{}')
        exc = ServiceException(http_resp=response)
        assert exc.is_server_error() is True

        # RateLimitExceededError
        response = MockHTTPResponse(429, "Too Many Requests", b'{}')
        exc = RateLimitExceededError(http_resp=response)
        assert exc.is_rate_limit_error() is True

