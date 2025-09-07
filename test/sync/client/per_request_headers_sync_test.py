"""
Test per-request custom HTTP headers functionality for sync client

This module tests the ability to send custom HTTP headers with individual API requests
using the synchronous client version.
"""

import json
from unittest import TestCase
from unittest.mock import ANY, patch

import urllib3

from openfga_sdk import rest
from openfga_sdk.client import ClientConfiguration
from openfga_sdk.sync import OpenFgaClient
from openfga_sdk.client.models.check_request import ClientCheckRequest
from openfga_sdk.client.models.tuple import ClientTuple
from openfga_sdk.client.models.write_request import ClientWriteRequest


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


class TestSyncPerRequestHeaders(TestCase):
    """Test per-request custom HTTP headers functionality for sync client"""

    def setUp(self):
        self.configuration = ClientConfiguration(
            api_url="http://api.fga.example",
            store_id=store_id,
            authorization_model_id=auth_model_id,
        )

    def tearDown(self):
        pass

    @patch.object(rest.RESTClientObject, "request")
    def test_sync_check_with_custom_headers(self, mock_request):
        """Test sync check request with custom headers"""
        response_body = '{"allowed": true}'
        mock_request.return_value = mock_response(response_body, 200)

        custom_headers = {
            "x-sync-correlation-id": "sync-test-correlation-123",
            "x-sync-trace-id": "sync-trace-456",
            "x-sync-custom-header": "sync-custom-value"
        }

        with OpenFgaClient(self.configuration) as fga_client:
            options = {
                "headers": custom_headers
            }
            
            body = ClientCheckRequest(
                user="user:test-user",
                relation="viewer",
                object="document:test-doc",
            )

            fga_client.check(body, options)

            # Verify the request was made with custom headers
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            headers = call_args.kwargs.get("headers", {})
            
            # Check that our custom headers were included
            self.assertEqual(headers["x-sync-correlation-id"], "sync-test-correlation-123")
            self.assertEqual(headers["x-sync-trace-id"], "sync-trace-456")
            self.assertEqual(headers["x-sync-custom-header"], "sync-custom-value")

    @patch.object(rest.RESTClientObject, "request")
    def test_sync_write_with_custom_headers(self, mock_request):
        """Test sync write request with custom headers"""
        response_body = '{}'
        mock_request.return_value = mock_response(response_body, 200)

        custom_headers = {
            "x-sync-request-id": "sync-write-request-789",
            "x-sync-client-version": "sync-1.0.0"
        }

        with OpenFgaClient(self.configuration) as fga_client:
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

            fga_client.write(body, options)

            # Verify the request was made with custom headers
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            headers = call_args.kwargs.get("headers", {})
            
            # Check that our custom headers were included
            self.assertEqual(headers["x-sync-request-id"], "sync-write-request-789")
            self.assertEqual(headers["x-sync-client-version"], "sync-1.0.0")

    @patch.object(rest.RESTClientObject, "request")
    def test_sync_multiple_requests_with_different_headers(self, mock_request):
        """Test that sync client can handle multiple requests with different headers"""
        response_body = '{"allowed": true}'
        mock_request.return_value = mock_response(response_body, 200)

        with OpenFgaClient(self.configuration) as fga_client:
            # First request with headers
            options1 = {
                "headers": {
                    "x-request-number": "1",
                    "x-operation": "first-check"
                }
            }
            
            body1 = ClientCheckRequest(
                user="user:test-user-1",
                relation="viewer",
                object="document:test-doc-1",
            )

            fga_client.check(body1, options1)

            # Second request with different headers
            options2 = {
                "headers": {
                    "x-request-number": "2",
                    "x-operation": "second-check"
                }
            }
            
            body2 = ClientCheckRequest(
                user="user:test-user-2",
                relation="editor",
                object="document:test-doc-2",
            )

            fga_client.check(body2, options2)

            # Verify both requests were made
            self.assertEqual(mock_request.call_count, 2)
            
            # Check first call headers
            first_call = mock_request.call_args_list[0]
            firstheaders = first_call.kwargs.get("headers", {})
            self.assertEqual(firstheaders["x-request-number"], "1")
            self.assertEqual(firstheaders["x-operation"], "first-check")
            
            # Check second call headers
            second_call = mock_request.call_args_list[1]
            secondheaders = second_call.kwargs.get("headers", {})
            self.assertEqual(secondheaders["x-request-number"], "2")
            self.assertEqual(secondheaders["x-operation"], "second-check")

    @patch.object(rest.RESTClientObject, "request")
    def test_sync_client_without_headers(self, mock_request):
        """Test that sync client works without headers option"""
        response_body = '{"allowed": true}'
        mock_request.return_value = mock_response(response_body, 200)

        with OpenFgaClient(self.configuration) as fga_client:
            # No options provided
            body = ClientCheckRequest(
                user="user:test-user",
                relation="viewer",
                object="document:test-doc",
            )

            fga_client.check(body)

            # Verify the request was made successfully
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            
            # When no headers provided, headers should still exist but be the default ones
            headers = call_args.kwargs.get("headers", {})
            # Default should include Content-Type but not our custom headers
            self.assertNotIn("x-custom-header", headers)

    @patch.object(rest.RESTClientObject, "request")
    def test_sync_client_empty_headers(self, mock_request):
        """Test that sync client works with empty headers"""
        response_body = '{"allowed": true}'
        mock_request.return_value = mock_response(response_body, 200)

        with OpenFgaClient(self.configuration) as fga_client:
            options = {
                "headers": {}
            }
            
            body = ClientCheckRequest(
                user="user:test-user",
                relation="viewer",
                object="document:test-doc",
            )

            fga_client.check(body, options)

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
    def test_sync_client_consistency_across_async_api(self, mock_request):
        """Test that sync client headers behavior is consistent with async client"""
        response_body = '{"allowed": true}'
        mock_request.return_value = mock_response(response_body, 200)

        # Test the same header pattern that works in async client
        custom_headers = {
            "x-correlation-id": "abc-123-def-456",
            "x-trace-id": "trace-789",
            "x-custom-header": "custom-value",
            "x-service-name": "authorization-service"
        }

        with OpenFgaClient(self.configuration) as fga_client:
            options = {
                "authorization_model_id": "custom-model-123",
                "headers": custom_headers
            }
            
            body = ClientCheckRequest(
                user="user:test-user",
                relation="viewer",
                object="document:test-doc",
            )

            fga_client.check(body, options)

            # Verify the request was made with custom headers
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            headers = call_args.kwargs.get("headers", {})
            
            # Check that all our custom headers were included
            self.assertEqual(headers["x-correlation-id"], "abc-123-def-456")
            self.assertEqual(headers["x-trace-id"], "trace-789")
            self.assertEqual(headers["x-custom-header"], "custom-value")
            self.assertEqual(headers["x-service-name"], "authorization-service")
            
            # Verify other options were also applied
            self.assertIsNotNone(call_args)
