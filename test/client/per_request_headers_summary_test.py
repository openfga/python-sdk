"""
Summary test to demonstrate per-request custom HTTP headers functionality

This test showcases the key functionality of sending custom headers with requests.
"""

import asyncio
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch

import urllib3

from openfga_sdk import rest
from openfga_sdk.client import ClientConfiguration
from openfga_sdk.client.client import OpenFgaClient
from openfga_sdk.client.models.check_request import ClientCheckRequest


def http_mock_response(body, status):
    headers = urllib3.response.HTTPHeaderDict(
        {"content-type": "application/json", "Fga-Request-Id": "test-request-id"}
    )
    return urllib3.HTTPResponse(
        body.encode("utf-8"), headers, status, preload_content=False
    )


def mock_response(body, status):
    obj = http_mock_response(body, status)
    return rest.RESTResponse(obj, obj.data)


class TestPerRequestHeadersSummary(IsolatedAsyncioTestCase):
    """Summary test for per-request custom HTTP headers"""

    def setUp(self):
        self.configuration = ClientConfiguration(
            api_url="http://api.fga.example",
            store_id="01YCP46JKYM8FJCQ37NMBYHE5X",
            authorization_model_id="01YCP46JKYM8FJCQ37NMBYHE6X",
        )

    @patch.object(rest.RESTClientObject, "request")
    async def test_per_request_headers_summary(self, mock_request):
        """Test that demonstrates per-request custom headers functionality"""
        response_body = '{"allowed": true}'
        mock_request.return_value = mock_response(response_body, 200)

        # Test custom headers for various use cases
        custom_headers = {
            "x-correlation-id": "req-123-abc",
            "x-trace-id": "trace-456-def",
            "x-client-version": "test-1.0.0",
            "x-service-name": "authorization-test",
            "x-environment": "test",
            "x-user-id": "test-admin",
        }

        async with OpenFgaClient(self.configuration) as fga_client:
            # Test with custom headers
            options = {
                "headers": custom_headers
            }

            body = ClientCheckRequest(
                user="user:test-user",
                relation="viewer",
                object="document:test-doc",
            )

            await fga_client.check(body, options)

            # Verify the request was made with all custom headers
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            headers = call_args.kwargs.get("headers", {})

            # Verify all custom headers are present
            for key, value in custom_headers.items():
                self.assertIn(key, headers, f"Header {key} should be present")
                self.assertEqual(headers[key], value, f"Header {key} should have value {value}")

            # Verify default headers are also present
            self.assertIn("Content-Type", headers)
            self.assertIn("Accept", headers)
            self.assertIn("User-Agent", headers)

            print("✅ Per-request custom headers test PASSED!")
            print(f"✅ Successfully sent {len(custom_headers)} custom headers:")
            for key, value in custom_headers.items():
                print(f"   {key}: {value}")


async def main():
    """Run the summary test"""
    test = TestPerRequestHeadersSummary()
    test.setUp()
    await test.test_per_request_headers_summary()


if __name__ == "__main__":
    asyncio.run(main())
