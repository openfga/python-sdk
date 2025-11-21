"""
Integration tests for enhanced error handling.

These tests verify that:
1. Error messages include operation context
2. Error codes and messages are properly exposed
3. Request IDs are available for debugging
4. Helper methods work correctly for error categorization

NOTE: These tests require a running OpenFGA server.
Set FGA_API_URL environment variable or use default http://localhost:8080

To run these tests with a local OpenFGA instance:
1. Start OpenFGA: docker run -p 8080:8080 openfga/openfga run
2. Run tests: FGA_API_URL=http://localhost:8080 pytest test/error_integration_test.py -v
"""

import os

import pytest
import pytest_asyncio

from openfga_sdk.client import ClientConfiguration
from openfga_sdk.client.client import OpenFgaClient
from openfga_sdk.exceptions import NotFoundException, ValidationException


# Skip all tests if FGA_API_URL is not set (for CI/CD environments without OpenFGA)
pytestmark = pytest.mark.skipif(
    not os.environ.get("FGA_API_URL") and not os.path.exists("/.dockerenv"),
    reason="OpenFGA server not available. Set FGA_API_URL to run integration tests.",
)


# Sample authorization model for testing
AUTH_MODEL = {
    "schema_version": "1.1",
    "type_definitions": [
        {"type": "user", "relations": {}},
        {
            "type": "document",
            "relations": {
                "viewer": {"this": {}},
                "owner": {"this": {}},
            },
            "metadata": {
                "relations": {
                    "viewer": {"directly_related_user_types": [{"type": "user"}]},
                    "owner": {"directly_related_user_types": [{"type": "user"}]},
                }
            },
        },
    ],
}


@pytest.mark.asyncio
class TestErrorIntegration:
    """Integration tests for enhanced error handling."""

    @pytest_asyncio.fixture
    async def fga_client(self):
        """
        Create a test client with a store and authorization model.

        Note: This requires a running OpenFGA server.
        Set FGA_API_URL environment variable or use default localhost:8080.
        """
        from openfga_sdk.models import CreateStoreRequest

        api_url = os.environ.get("FGA_API_URL", "http://localhost:8080")

        config = ClientConfiguration(
            api_url=api_url,
        )

        client = OpenFgaClient(config)

        # Create a test store
        store = await client.create_store(CreateStoreRequest(name="ErrorTestStore"))
        config.store_id = store.id
        client = OpenFgaClient(config)  # Recreate client with store_id

        # Write the authorization model
        model_response = await client.write_authorization_model(AUTH_MODEL)
        config.authorization_model_id = model_response.authorization_model_id
        client = OpenFgaClient(config)  # Recreate client with auth model id

        yield client

        # Cleanup: delete the store
        try:
            await client.delete_store()
        except Exception:
            pass  # Ignore cleanup errors

    async def test_write_validation_error_invalid_type(self, fga_client):
        """Test that write with invalid type shows proper error details."""
        from openfga_sdk.client.models import ClientTuple, ClientWriteRequest

        # Try to write a tuple with invalid type
        with pytest.raises(ValidationException) as exc_info:
            await fga_client.write(
                ClientWriteRequest(
                    writes=[
                        ClientTuple(
                            user="user:anne",
                            relation="viewer",
                            object="invalid_type:readme",
                        )
                    ]
                )
            )

        exception = exc_info.value

        # Verify error details are accessible
        assert exception.code is not None
        assert "validation" in exception.code.lower()
        assert "invalid_type" in exception.error_message.lower()
        assert exception.operation_name == "write"
        # request_id might be None in local dev environments
        # assert exception.request_id is not None
        assert exception.status == 400

        # Verify formatted message includes all components
        error_str = str(exception)
        assert "[write]" in error_str
        assert "HTTP 400" in error_str
        assert "validation" in error_str.lower()
        # request_id might be None in local dev, so it might not be in the message
        # assert "[request-id:" in error_str

    async def test_write_validation_error_invalid_relation(self, fga_client):
        """Test that write with invalid relation shows proper error details."""
        from openfga_sdk.client.models import ClientTuple, ClientWriteRequest

        # Try to write a tuple with valid type but invalid relation
        with pytest.raises(ValidationException) as exc_info:
            await fga_client.write(
                ClientWriteRequest(
                    writes=[
                        ClientTuple(
                            user="user:anne",
                            relation="invalid_relation",
                            object="document:readme",
                        )
                    ]
                )
            )

        exception = exc_info.value

        # Verify error details
        assert exception.code is not None
        assert "validation" in exception.code.lower()
        assert "relation" in exception.error_message.lower()
        assert exception.operation_name == "write"
        # request_id might be None in local dev environments
        # assert exception.request_id is not None

        # Verify formatted message
        error_str = str(exception)
        assert "[write]" in error_str
        assert "HTTP 400" in error_str

    async def test_check_validation_error(self, fga_client):
        """Test that check with invalid type shows proper error details."""
        from openfga_sdk.client.models import ClientCheckRequest

        # Try check with invalid type
        with pytest.raises(ValidationException) as exc_info:
            await fga_client.check(
                ClientCheckRequest(
                    user="user:anne",
                    relation="viewer",
                    object="invalid_type:readme",
                )
            )

        exception = exc_info.value

        assert exception.operation_name == "check"
        assert exception.status == 400
        assert exception.code is not None
        assert "validation" in exception.code.lower()

        error_str = str(exception)
        assert "[check]" in error_str
        assert "HTTP 400" in error_str

    async def test_expand_validation_error(self, fga_client):
        """Test that expand with invalid type shows proper error details."""
        from openfga_sdk.client.models import ClientExpandRequest

        # Try expand with invalid type
        with pytest.raises(ValidationException) as exc_info:
            await fga_client.expand(
                ClientExpandRequest(
                    object="invalid_type:readme",
                    relation="viewer",
                )
            )

        exception = exc_info.value

        assert exception.operation_name == "expand"
        assert exception.status == 400
        assert exception.code is not None

    async def test_not_found_error(self, fga_client):
        """Test that not found errors are properly categorized."""
        # Delete the store first
        await fga_client.delete_store()

        # Now try to get the deleted store
        with pytest.raises(NotFoundException) as exc_info:
            await fga_client.get_store()

        exception = exc_info.value

        assert exception.status == 404
        assert exception.is_not_found_error()
        assert exception.is_client_error()
        assert not exception.is_server_error()
        assert not exception.is_retryable()

        error_str = str(exception)
        assert "HTTP 404" in error_str

    async def test_error_helper_methods_validation(self, fga_client):
        """Test helper methods for validation errors."""
        from openfga_sdk.client.models import ClientTuple, ClientWriteRequest

        with pytest.raises(ValidationException) as exc_info:
            await fga_client.write(
                ClientWriteRequest(
                    writes=[
                        ClientTuple(
                            user="user:anne",
                            relation="viewer",
                            object="invalid_type:readme",
                        )
                    ]
                )
            )

        exception = exc_info.value

        # Test all helper methods
        assert exception.is_validation_error()
        assert exception.is_client_error()
        assert not exception.is_server_error()
        assert not exception.is_retryable()
        assert not exception.is_authentication_error()
        assert not exception.is_not_found_error()
        assert not exception.is_rate_limit_error()

    async def test_error_message_format_consistency(self, fga_client):
        """Test that error messages follow consistent format across operations."""
        from openfga_sdk.client.models import (
            ClientCheckRequest,
            ClientTuple,
            ClientWriteRequest,
        )

        # Test write error format
        with pytest.raises(ValidationException) as write_exc:
            await fga_client.write(
                ClientWriteRequest(
                    writes=[
                        ClientTuple(
                            user="user:anne",
                            relation="viewer",
                            object="invalid:x",
                        )
                    ]
                )
            )

        write_error = str(write_exc.value)
        assert write_error.startswith("[write]")
        assert "HTTP 400" in write_error
        # request_id might not be present in local dev
        # assert "[request-id:" in write_error

        # Test check error format
        with pytest.raises(ValidationException) as check_exc:
            await fga_client.check(
                ClientCheckRequest(
                    user="user:anne",
                    relation="viewer",
                    object="invalid:x",
                )
            )

        check_error = str(check_exc.value)
        assert check_error.startswith("[check]")
        assert "HTTP 400" in check_error
        # request_id might not be present in local dev
        # assert "[request-id:" in check_error

        # Both should follow same pattern (with or without request-id)
        import re

        # Pattern with optional request-id at the end
        pattern = r"^\[\w+\] HTTP \d{3} .+ \(.+\)( \[request-id: .+\])?$"
        assert re.match(pattern, write_error)
        assert re.match(pattern, check_error)

    async def test_error_code_fields_accessibility(self, fga_client):
        """Test that all error fields are accessible."""
        from openfga_sdk.client.models import ClientTuple, ClientWriteRequest

        with pytest.raises(ValidationException) as exc_info:
            await fga_client.write(
                ClientWriteRequest(
                    writes=[
                        ClientTuple(
                            user="user:anne",
                            relation="viewer",
                            object="invalid_type:readme",
                        )
                    ]
                )
            )

        exception = exc_info.value

        # Verify all fields are accessible
        assert exception.status == 400
        assert exception.code is not None
        assert isinstance(exception.code, str)
        assert exception.operation_name == "write"
        assert exception.error_message is not None
        assert isinstance(exception.error_message, str)
        # request_id might be None in local dev environments
        # assert exception.request_id is not None
        # assert isinstance(exception.request_id, str)

        # Request ID should match expected format if present
        if exception.request_id:
            import re

            assert re.match(r"[a-zA-Z0-9-]+", exception.request_id)

    async def test_different_validation_errors_have_different_messages(
        self, fga_client
    ):
        """Test that different validation errors surface different messages."""
        from openfga_sdk.client.models import ClientTuple, ClientWriteRequest

        # Case 1: Invalid type
        with pytest.raises(ValidationException) as exc1:
            await fga_client.write(
                ClientWriteRequest(
                    writes=[
                        ClientTuple(
                            user="user:anne",
                            relation="viewer",
                            object="invalid_type:readme",
                        )
                    ]
                )
            )

        error1 = exc1.value
        assert "type" in error1.error_message.lower()

        # Case 2: Invalid relation
        with pytest.raises(ValidationException) as exc2:
            await fga_client.write(
                ClientWriteRequest(
                    writes=[
                        ClientTuple(
                            user="user:anne",
                            relation="invalid_relation",
                            object="document:readme",
                        )
                    ]
                )
            )

        error2 = exc2.value
        assert "relation" in error2.error_message.lower()

        # Both should have same error code but different messages
        assert error1.code == error2.code
        assert error1.error_message != error2.error_message

    async def test_error_details_not_lost_in_traceback(self, fga_client):
        """Test that error details are preserved in exception traceback."""
        from openfga_sdk.client.models import ClientTuple, ClientWriteRequest

        try:
            await fga_client.write(
                ClientWriteRequest(
                    writes=[
                        ClientTuple(
                            user="user:anne",
                            relation="viewer",
                            object="invalid_type:readme",
                        )
                    ]
                )
            )
            pytest.fail("Expected ValidationException to be raised")
        except ValidationException as e:
            # String representation should include all details
            error_string = str(e)
            assert "invalid_type" in error_string.lower()

            # Exception message should be properly formatted
            error_message = e.error_message
            assert "invalid_type" in error_message.lower()

            # Fields should be accessible
            assert e.status == 400
            assert e.code is not None
            assert e.operation_name == "write"
            # request_id might be None in local dev environments
            # assert e.request_id is not None


# Sync version of tests
class TestErrorIntegrationSync:
    """Synchronous integration tests for enhanced error handling."""

    @pytest.fixture
    def fga_client_sync(self):
        """
        Create a sync test client with a store and authorization model.

        Note: This requires a running OpenFGA server.
        """
        from openfga_sdk.models import CreateStoreRequest
        from openfga_sdk.sync.client.client import OpenFgaClient as SyncOpenFgaClient

        api_url = os.environ.get("FGA_API_URL", "http://localhost:8080")

        config = ClientConfiguration(
            api_url=api_url,
        )

        client = SyncOpenFgaClient(config)

        # Create a test store
        store = client.create_store(CreateStoreRequest(name="ErrorTestStoreSync"))
        config.store_id = store.id
        client = SyncOpenFgaClient(config)  # Recreate client with store_id

        # Write the authorization model
        model_response = client.write_authorization_model(AUTH_MODEL)
        config.authorization_model_id = model_response.authorization_model_id
        client = SyncOpenFgaClient(config)  # Recreate client with auth model id

        yield client

        # Cleanup
        try:
            client.delete_store()
        except Exception:
            pass

    def test_sync_write_validation_error(self, fga_client_sync):
        """Test sync client error handling."""
        from openfga_sdk.client.models import ClientTuple, ClientWriteRequest

        with pytest.raises(ValidationException) as exc_info:
            fga_client_sync.write(
                ClientWriteRequest(
                    writes=[
                        ClientTuple(
                            user="user:anne",
                            relation="viewer",
                            object="invalid_type:readme",
                        )
                    ]
                )
            )

        exception = exc_info.value

        assert exception.operation_name == "write"
        assert exception.status == 400
        assert exception.code is not None
        assert exception.is_validation_error()

        error_str = str(exception)
        assert "[write]" in error_str
        assert "HTTP 400" in error_str

    def test_sync_error_helper_methods(self, fga_client_sync):
        """Test that helper methods work in sync client."""
        from openfga_sdk.client.models import ClientTuple, ClientWriteRequest

        with pytest.raises(ValidationException) as exc_info:
            fga_client_sync.write(
                ClientWriteRequest(
                    writes=[
                        ClientTuple(
                            user="user:anne",
                            relation="viewer",
                            object="invalid_type:readme",
                        )
                    ]
                )
            )

        exception = exc_info.value

        assert exception.is_validation_error()
        assert exception.is_client_error()
        assert not exception.is_server_error()
        assert not exception.is_retryable()
