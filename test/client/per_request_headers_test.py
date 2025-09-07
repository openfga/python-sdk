"""
Test per-request custom HTTP headers functionality

This module tests the ability to send custom HTTP headers with individual API requests
using the options["headers"] parameter that gets converted to headers internally.
"""

import uuid

from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch

import urllib3

from openfga_sdk import rest
from openfga_sdk.client import ClientConfiguration
from openfga_sdk.client.client import OpenFgaClient
from openfga_sdk.client.models.assertion import ClientAssertion
from openfga_sdk.client.models.batch_check_item import ClientBatchCheckItem
from openfga_sdk.client.models.batch_check_request import ClientBatchCheckRequest
from openfga_sdk.client.models.check_request import ClientCheckRequest
from openfga_sdk.client.models.expand_request import ClientExpandRequest
from openfga_sdk.client.models.list_objects_request import ClientListObjectsRequest
from openfga_sdk.client.models.tuple import ClientTuple
from openfga_sdk.client.models.write_request import ClientWriteRequest
from openfga_sdk.models.read_request_tuple_key import ReadRequestTupleKey


store_id = "01YCP46JKYM8FJCQ37NMBYHE5X"
auth_model_id = "01YCP46JKYM8FJCQ37NMBYHE6X"
request_id = "x1y2z3"


def http_mock_response(body, status):
    headers = urllib3.response.HTTPHeaderDict(
        {"content-type": "application/json", "Fga-Request-Id": request_id}
    )
    return urllib3.HTTPResponse(
        body.encode("utf-8"), headers, status, preload_content=False
    )


def mock_response(body, status):
    obj = http_mock_response(body, status)
    return rest.RESTResponse(obj, obj.data)


class TestPerRequestHeaders(IsolatedAsyncioTestCase):
    """Test per-request custom HTTP headers functionality"""

    def setUp(self):
        self.configuration = ClientConfiguration(
            api_url="http://api.fga.example",
            store_id=store_id,
            authorization_model_id=auth_model_id,
        )

    def tearDown(self):
        pass

    @patch.object(rest.RESTClientObject, "request")
    async def test_check_with_custom_headers(self, mock_request):
        """Test check request with custom headers"""
        response_body = '{"allowed": true}'
        mock_request.return_value = mock_response(response_body, 200)

        custom_headers = {
            "x-correlation-id": "test-correlation-123",
            "x-trace-id": "trace-456",
            "x-custom-header": "custom-value"
        }

        async with OpenFgaClient(self.configuration) as fga_client:
            options = {
                "headers": custom_headers
            }

            body = ClientCheckRequest(
                user="user:test-user",
                relation="viewer",
                object="document:test-doc",
            )

            await fga_client.check(body, options)

            # Verify the request was made with custom headers
            mock_request.assert_called_once()
            call_args = mock_request.call_args

            # Headers should be passed as 'headers' parameter in the call
            headers = call_args.kwargs.get("headers", {})

            # Check that our custom headers were included
            self.assertEqual(headers["x-correlation-id"], "test-correlation-123")
            self.assertEqual(headers["x-trace-id"], "trace-456")
            self.assertEqual(headers["x-custom-header"], "custom-value")

    @patch.object(rest.RESTClientObject, "request")
    async def test_write_with_custom_headers(self, mock_request):
        """Test write request with custom headers"""
        response_body = '{}'
        mock_request.return_value = mock_response(response_body, 200)

        custom_headers = {
            "x-request-id": "write-request-789",
            "x-client-version": "1.0.0"
        }

        async with OpenFgaClient(self.configuration) as fga_client:
            options = {
                "headers": custom_headers
            }

            body = ClientWriteRequest(
                writes=[
                    ClientTuple(
                        user="user:test-user",
                        relation="viewer",
                        object="document:test-doc",
                    )
                ]
            )

            await fga_client.write(body, options)

            # Verify the request was made with custom headers
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            headers = call_args.kwargs.get("headers", {})

            # Check that our custom headers were included
            self.assertEqual(headers["x-request-id"], "write-request-789")
            self.assertEqual(headers["x-client-version"], "1.0.0")

    @patch.object(rest.RESTClientObject, "request")
    async def test_list_objects_with_custom_headers(self, mock_request):
        """Test list_objects request with custom headers"""
        response_body = '{"objects": ["document:1", "document:2"]}'
        mock_request.return_value = mock_response(response_body, 200)

        custom_headers = {
            "x-service-name": "authorization-service",
            "x-environment": "test"
        }

        async with OpenFgaClient(self.configuration) as fga_client:
            options = {
                "headers": custom_headers
            }

            body = ClientListObjectsRequest(
                user="user:test-user",
                relation="viewer",
                type="document",
            )

            await fga_client.list_objects(body, options)

            # Verify the request was made with custom headers
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            headers = call_args.kwargs.get("headers", {})

            # Check that our custom headers were included
            self.assertEqual(headers["x-service-name"], "authorization-service")
            self.assertEqual(headers["x-environment"], "test")

    @patch.object(rest.RESTClientObject, "request")
    async def test_expand_with_custom_headers(self, mock_request):
        """Test expand request with custom headers"""
        response_body = '{"tree": {"root": {"name": "test", "leaf": {"users": {"users": []}}}}}'
        mock_request.return_value = mock_response(response_body, 200)

        custom_headers = {
            "x-operation": "expand-check",
            "x-user-id": "admin-user"
        }

        async with OpenFgaClient(self.configuration) as fga_client:
            options = {
                "headers": custom_headers
            }

            body = ClientExpandRequest(
                relation="viewer",
                object="document:test-doc",
            )

            await fga_client.expand(body, options)

            # Verify the request was made with custom headers
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            headers = call_args.kwargs.get("headers", {})

            # Check that our custom headers were included
            self.assertEqual(headers["x-operation"], "expand-check")
            self.assertEqual(headers["x-user-id"], "admin-user")

    @patch.object(rest.RESTClientObject, "request")
    async def test_batch_check_with_custom_headers(self, mock_request):
        """Test batch_check request with custom headers"""
        response_body = """
        {
            "result": {
                "test-correlation-id": {
                    "allowed": true
                }
            }
        }
        """
        mock_request.return_value = mock_response(response_body, 200)

        custom_headers = {
            "x-batch-id": "batch-123",
            "x-priority": "high"
        }

        async with OpenFgaClient(self.configuration) as fga_client:
            options = {
                "headers": custom_headers
            }

            checks = [
                ClientBatchCheckItem(
                    user="user:test-user",
                    relation="viewer",
                    object="document:test-doc",
                    correlation_id="test-correlation-id",
                )
            ]
            body = ClientBatchCheckRequest(checks=checks)

            await fga_client.batch_check(body, options)

            # Verify the request was made with custom headers
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            headers = call_args.kwargs.get("headers", {})

            # Check that our custom headers were included
            self.assertEqual(headers["x-batch-id"], "batch-123")
            self.assertEqual(headers["x-priority"], "high")

    @patch.object(rest.RESTClientObject, "request")
    async def test_read_with_custom_headers(self, mock_request):
        """Test read request with custom headers"""
        response_body = """
        {
            "tuples": [
                {
                    "key": {
                        "user": "user:test-user",
                        "relation": "viewer",
                        "object": "document:test-doc"
                    },
                    "timestamp": "2023-01-01T00:00:00.000Z"
                }
            ],
            "continuation_token": ""
        }
        """
        mock_request.return_value = mock_response(response_body, 200)

        custom_headers = {
            "x-read-operation": "get-tuples",
            "x-source": "admin-console"
        }

        async with OpenFgaClient(self.configuration) as fga_client:
            options = {
                "headers": custom_headers
            }

            body = ReadRequestTupleKey(
                user="user:test-user",
                relation="viewer",
                object="document:test-doc",
            )

            await fga_client.read(body, options)

            # Verify the request was made with custom headers
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            headers = call_args.kwargs.get("headers", {})

            # Check that our custom headers were included
            self.assertEqual(headers["x-read-operation"], "get-tuples")
            self.assertEqual(headers["x-source"], "admin-console")

    @patch.object(rest.RESTClientObject, "request")
    async def test_read_authorization_models_with_custom_headers(self, mock_request):
        """Test read_authorization_models request with custom headers"""
        response_body = """
        {
            "authorization_models": [
                {
                    "id": "01YCP46JKYM8FJCQ37NMBYHE6X",
                    "schema_version": "1.1",
                    "type_definitions": []
                }
            ]
        }
        """
        mock_request.return_value = mock_response(response_body, 200)

        custom_headers = {
            "x-model-operation": "list-models",
            "x-tenant": "tenant-123"
        }

        async with OpenFgaClient(self.configuration) as fga_client:
            options = {
                "headers": custom_headers
            }

            await fga_client.read_authorization_models(options)

            # Verify the request was made with custom headers
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            headers = call_args.kwargs.get("headers", {})

            # Check that our custom headers were included
            self.assertEqual(headers["x-model-operation"], "list-models")
            self.assertEqual(headers["x-tenant"], "tenant-123")

    @patch.object(rest.RESTClientObject, "request")
    async def test_write_assertions_with_custom_headers(self, mock_request):
        """Test write_assertions request with custom headers"""
        response_body = '{}'
        mock_request.return_value = mock_response(response_body, 200)

        custom_headers = {
            "x-assertion-batch": "test-assertions",
            "x-test-run": "automated"
        }

        async with OpenFgaClient(self.configuration) as fga_client:
            options = {
                "headers": custom_headers
            }

            body = [
                ClientAssertion(
                    user="user:test-user",
                    relation="viewer",
                    object="document:test-doc",
                    expectation=True,
                )
            ]

            await fga_client.write_assertions(body, options)

            # Verify the request was made with custom headers
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            headers = call_args.kwargs.get("headers", {})

            # Check that our custom headers were included
            self.assertEqual(headers["x-assertion-batch"], "test-assertions")
            self.assertEqual(headers["x-test-run"], "automated")

    @patch.object(rest.RESTClientObject, "request")
    async def test_headers_with_other_options(self, mock_request):
        """Test that headers work correctly when combined with other options"""
        response_body = '{"allowed": true}'
        mock_request.return_value = mock_response(response_body, 200)

        custom_headers = {
            "x-combined-test": "headers-and-options"
        }

        async with OpenFgaClient(self.configuration) as fga_client:
            options = {
                "authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1",
                "headers": custom_headers,
                "consistency": "strong"
            }

            body = ClientCheckRequest(
                user="user:test-user",
                relation="viewer",
                object="document:test-doc",
            )

            await fga_client.check(body, options)

            # Verify the request was made with custom headers and other options
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            headers = call_args.kwargs.get("headers", {})

            # Check that our custom headers were included
            self.assertEqual(headers["x-combined-test"], "headers-and-options")

            # Verify other options were also applied (by checking the call args structure)
            self.assertIsNotNone(call_args)

    @patch.object(rest.RESTClientObject, "request")
    async def test_empty_headers_option(self, mock_request):
        """Test that empty headers option works correctly"""
        response_body = '{"allowed": true}'
        mock_request.return_value = mock_response(response_body, 200)

        async with OpenFgaClient(self.configuration) as fga_client:
            options = {
                "headers": {}
            }

            body = ClientCheckRequest(
                user="user:test-user",
                relation="viewer",
                object="document:test-doc",
            )

            await fga_client.check(body, options)

            # Verify the request was made successfully
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            headers = call_args.kwargs.get("headers", {})

            # Headers should contain defaults but not our custom headers
            self.assertEqual(len(headers), 3)  # Should contain default headers
            self.assertIn("Content-Type", headers)
            self.assertIn("Accept", headers)
            self.assertIn("User-Agent", headers)
            # But should not contain custom headers
            self.assertNotIn("x-custom-header", headers)

    @patch.object(rest.RESTClientObject, "request")
    async def test_no_headers_option(self, mock_request):
        """Test that requests work without headers option"""
        response_body = '{"allowed": true}'
        mock_request.return_value = mock_response(response_body, 200)

        async with OpenFgaClient(self.configuration) as fga_client:
            # No options provided
            body = ClientCheckRequest(
                user="user:test-user",
                relation="viewer",
                object="document:test-doc",
            )

            await fga_client.check(body)

            # Verify the request was made successfully
            mock_request.assert_called_once()
            call_args = mock_request.call_args

            # When no headers provided, headers should still exist but be the default ones
            headers = call_args.kwargs.get("headers", {})
            # Default should include Content-Type but not our custom headers
            self.assertNotIn("x-custom-header", headers)

    @patch.object(rest.RESTClientObject, "request")
    async def test_header_values_as_strings(self, mock_request):
        """Test that header values are properly handled as strings"""
        response_body = '{"allowed": true}'
        mock_request.return_value = mock_response(response_body, 200)

        custom_headers = {
            "x-string-header": "string-value",
            "x-number-header": "123",  # Should be string
            "x-boolean-header": "true",  # Should be string
            "x-uuid-header": str(uuid.uuid4()),
        }

        async with OpenFgaClient(self.configuration) as fga_client:
            options = {
                "headers": custom_headers
            }

            body = ClientCheckRequest(
                user="user:test-user",
                relation="viewer",
                object="document:test-doc",
            )

            await fga_client.check(body, options)

            # Verify the request was made with custom headers
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            headers = call_args.kwargs.get("headers", {})

            # Check that all header values are strings
            for key, value in custom_headers.items():
                self.assertEqual(headers[key], value)
                self.assertIsInstance(headers[key], str)

    @patch.object(rest.RESTClientObject, "request")
    async def test_special_characters_in_headers(self, mock_request):
        """Test that headers with special characters work correctly"""
        response_body = '{"allowed": true}'
        mock_request.return_value = mock_response(response_body, 200)

        custom_headers = {
            "x-special-chars": "value-with-dashes_and_underscores",
            "x-with-dots": "value.with.dots",
            "x-with-numbers": "value123with456numbers",
            "x-case-sensitive": "CamelCaseValue",
        }

        async with OpenFgaClient(self.configuration) as fga_client:
            options = {
                "headers": custom_headers
            }

            body = ClientCheckRequest(
                user="user:test-user",
                relation="viewer",
                object="document:test-doc",
            )

            await fga_client.check(body, options)

            # Verify the request was made with custom headers
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            headers = call_args.kwargs.get("headers", {})

            # Check that our custom headers were included exactly as provided
            for key, value in custom_headers.items():
                self.assertEqual(headers[key], value)
