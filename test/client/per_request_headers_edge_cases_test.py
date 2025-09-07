"""
Test edge cases and error scenarios for per-request custom HTTP headers functionality

This module tests edge cases, invalid inputs, and error scenarios for the
per-request headers feature to ensure robust handling.
"""

from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch

import urllib3

from openfga_sdk import rest
from openfga_sdk.client import ClientConfiguration
from openfga_sdk.client.client import (
    OpenFgaClient,
    options_to_kwargs,
    set_heading_if_not_set,
)
from openfga_sdk.client.models.check_request import ClientCheckRequest


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


class TestPerRequestHeadersEdgeCases(IsolatedAsyncioTestCase):
    """Test edge cases and error scenarios for per-request headers"""

    def setUp(self):
        self.configuration = ClientConfiguration(
            api_url="http://api.fga.example",
            store_id=store_id,
            authorization_model_id=auth_model_id,
        )

    def tearDown(self):
        pass

    def test_options_to_kwargs_with_headers(self):
        """Test options_to_kwargs function properly handles headers"""
        options = {
            "headers": {
                "x-test-header": "test-value",
                "x-another": "another-value"
            },
            "authorization_model_id": "test-model",
            "page_size": 25
        }

        result = options_to_kwargs(options)

        # Check that headers are converted to _headers
        self.assertIn("_headers", result)
        self.assertEqual(result["_headers"]["x-test-header"], "test-value")
        self.assertEqual(result["_headers"]["x-another"], "another-value")

        # Check that other options are preserved
        self.assertEqual(result.get("page_size"), 25)

    def test_options_to_kwargs_without_headers(self):
        """Test options_to_kwargs function works without headers"""
        options = {
            "authorization_model_id": "test-model",
            "page_size": 25
        }

        result = options_to_kwargs(options)

        # Check that headers is not present when no headers option
        self.assertNotIn("headers", result)

        # Check that other options are preserved
        self.assertEqual(result.get("page_size"), 25)

    def test_options_to_kwargs_with_none(self):
        """Test options_to_kwargs function handles None input"""
        result = options_to_kwargs(None)

        # Should return empty dict
        self.assertEqual(result, {})

    def test_options_to_kwargs_with_empty_dict(self):
        """Test options_to_kwargs function handles empty dict input"""
        result = options_to_kwargs({})

        # Should return empty dict
        self.assertEqual(result, {})

    def test_set_heading_if_not_set_with_existing_headers(self):
        """Test set_heading_if_not_set function with existing headers"""
        options = {
            "headers": {
                "x-existing": "existing-value"
            }
        }

        result = set_heading_if_not_set(options, "x-new-header", "new-value")

        # Check that new header was added
        self.assertEqual(result["headers"]["x-new-header"], "new-value")
        # Check that existing header is preserved
        self.assertEqual(result["headers"]["x-existing"], "existing-value")

    def test_set_heading_if_not_set_without_headers(self):
        """Test set_heading_if_not_set function when headers dict doesn't exist"""
        options = {
            "other_option": "value"
        }

        result = set_heading_if_not_set(options, "x-new-header", "new-value")

        # Check that headers dict was created and header was added
        self.assertIn("headers", result)
        self.assertEqual(result["headers"]["x-new-header"], "new-value")
        # Check that other options are preserved
        self.assertEqual(result["other_option"], "value")

    def test_set_heading_if_not_set_with_none_options(self):
        """Test set_heading_if_not_set function with None options"""
        result = set_heading_if_not_set(None, "x-new-header", "new-value")

        # Check that options dict was created with headers
        self.assertIn("headers", result)
        self.assertEqual(result["headers"]["x-new-header"], "new-value")

    def test_set_heading_if_not_set_header_already_exists(self):
        """Test set_heading_if_not_set function when header already exists"""
        options = {
            "headers": {
                "x-existing": "original-value"
            }
        }

        result = set_heading_if_not_set(options, "x-existing", "new-value")

        # Check that original value is preserved (not overwritten)
        self.assertEqual(result["headers"]["x-existing"], "original-value")

    def test_set_heading_if_not_set_with_invalidheaders_type(self):
        """Test set_heading_if_not_set function with invalid headers type"""
        options = {
            "headers": "not-a-dict"  # Invalid type
        }

        result = set_heading_if_not_set(options, "x-new-header", "new-value")

        # Function should create new headers dict, replacing the invalid one
        self.assertIsInstance(result["headers"], dict)
        self.assertEqual(result["headers"]["x-new-header"], "new-value")

    @patch.object(rest.RESTClientObject, "request")
    async def test_headers_with_invalid_type_in_options(self, mock_request):
        """Test that invalid headers type in options is handled gracefully"""
        response_body = '{"allowed": true}'
        mock_request.return_value = mock_response(response_body, 200)

        # This should be handled gracefully - converted to dict or ignored
        options_with_invalidheaders = {
            "headers": "not-a-dict"
        }

        async with OpenFgaClient(self.configuration) as fga_client:
            body = ClientCheckRequest(
                user="user:test-user",
                relation="viewer",
                object="document:test-doc",
            )

            # This should not raise an exception
            await fga_client.check(body, options_with_invalidheaders)

            # Verify the request was made
            mock_request.assert_called_once()

    @patch.object(rest.RESTClientObject, "request")
    async def test_large_number_of_headers(self, mock_request):
        """Test that a large number of headers is handled correctly"""
        response_body = '{"allowed": true}'
        mock_request.return_value = mock_response(response_body, 200)

        # Create a large number of headers
        largeheaders = {f"x-header-{i}": f"value-{i}" for i in range(100)}

        async with OpenFgaClient(self.configuration) as fga_client:
            options = {
                "headers": largeheaders
            }

            body = ClientCheckRequest(
                user="user:test-user",
                relation="viewer",
                object="document:test-doc",
            )

            await fga_client.check(body, options)

            # Verify the request was made with all headers
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            headers = call_args.kwargs.get("headers", {})

            # Check that all custom headers were included (plus system headers)
            self.assertGreaterEqual(len(headers), 100)
            for i in range(100):
                self.assertEqual(headers[f"x-header-{i}"], f"value-{i}")

    @patch.object(rest.RESTClientObject, "request")
    async def test_unicode_headers(self, mock_request):
        """Test that unicode characters in headers are handled correctly"""
        response_body = '{"allowed": true}'
        mock_request.return_value = mock_response(response_body, 200)

        unicode_headers = {
            "x-unicode-header": "测试值",  # Chinese characters
            "x-emoji-header": "🚀🔐",  # Emojis
            "x-accented-header": "café-résumé",  # Accented characters
        }

        async with OpenFgaClient(self.configuration) as fga_client:
            options = {
                "headers": unicode_headers
            }

            body = ClientCheckRequest(
                user="user:test-user",
                relation="viewer",
                object="document:test-doc",
            )

            await fga_client.check(body, options)

            # Verify the request was made with unicode headers
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            headers = call_args.kwargs.get("headers", {})

            # Check that unicode headers were included
            self.assertEqual(headers["x-unicode-header"], "测试值")
            self.assertEqual(headers["x-emoji-header"], "🚀🔐")
            self.assertEqual(headers["x-accented-header"], "café-résumé")

    @patch.object(rest.RESTClientObject, "request")
    async def test_long_header_values(self, mock_request):
        """Test that very long header values are handled correctly"""
        response_body = '{"allowed": true}'
        mock_request.return_value = mock_response(response_body, 200)

        # Create a very long header value
        long_value = "x" * 10000  # 10KB header value

        longheaders = {
            "x-long-header": long_value,
            "x-normal-header": "normal-value"
        }

        async with OpenFgaClient(self.configuration) as fga_client:
            options = {
                "headers": longheaders
            }

            body = ClientCheckRequest(
                user="user:test-user",
                relation="viewer",
                object="document:test-doc",
            )

            await fga_client.check(body, options)

            # Verify the request was made with long headers
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            headers = call_args.kwargs.get("headers", {})

            # Check that long header was included
            self.assertEqual(headers["x-long-header"], long_value)
            self.assertEqual(headers["x-normal-header"], "normal-value")

    @patch.object(rest.RESTClientObject, "request")
    async def test_header_case_sensitivity(self, mock_request):
        """Test that header case is preserved"""
        response_body = '{"allowed": true}'
        mock_request.return_value = mock_response(response_body, 200)

        case_sensitiveheaders = {
            "X-Upper-Case": "upper-value",
            "x-lower-case": "lower-value",
            "X-Mixed-Case": "mixed-value",
            "x-WEIRD-cAsE": "weird-value"
        }

        async with OpenFgaClient(self.configuration) as fga_client:
            options = {
                "headers": case_sensitiveheaders
            }

            body = ClientCheckRequest(
                user="user:test-user",
                relation="viewer",
                object="document:test-doc",
            )

            await fga_client.check(body, options)

            # Verify the request was made with case-preserved headers
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            headers = call_args.kwargs.get("headers", {})

            # Check that header case was preserved
            self.assertEqual(headers["X-Upper-Case"], "upper-value")
            self.assertEqual(headers["x-lower-case"], "lower-value")
            self.assertEqual(headers["X-Mixed-Case"], "mixed-value")
            self.assertEqual(headers["x-WEIRD-cAsE"], "weird-value")

    @patch.object(rest.RESTClientObject, "request")
    async def test_header_overrides_default_headers(self, mock_request):
        """Test that custom headers can override overrideable default headers"""
        response_body = '{"allowed": true}'
        mock_request.return_value = mock_response(response_body, 200)

        # Test with headers that can override defaults (User-Agent)
        # Note: Accept and Content-Type are set by the API method and cannot be overridden
        override_headers = {
            "User-Agent": "custom-user-agent",
            "x-custom-header": "custom-value",
            "Authorization": "Bearer custom-token",
        }

        async with OpenFgaClient(self.configuration) as fga_client:
            options = {
                "headers": override_headers
            }

            body = ClientCheckRequest(
                user="user:test-user",
                relation="viewer",
                object="document:test-doc",
            )

            await fga_client.check(body, options)

            # Verify the request was made
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            headers = call_args.kwargs.get("headers", {})

            # Check that overrideable custom headers work
            self.assertEqual(headers["User-Agent"], "custom-user-agent")
            self.assertEqual(headers["x-custom-header"], "custom-value")
            self.assertEqual(headers["Authorization"], "Bearer custom-token")

            # System headers are still set by the API method
            self.assertEqual(headers["Accept"], "application/json")
            self.assertTrue("Content-Type" in headers)
