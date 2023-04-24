from unittest import IsolatedAsyncioTestCase

import urllib3

import openfga_sdk
from openfga_sdk import CheckResponse, rest, ClientCheckRequest, ClientCheckRequestOpts

from unittest.mock import ANY, patch

from openfga_sdk.client import open_fga_client

store_id = 'd12345abc'
request_id = 'x1y2z3'

def http_mock_response(body, status):
    headers = urllib3.response.HTTPHeaderDict({
        'content-type': 'application/json',
        'Fga-Request-Id': request_id
    })
    return urllib3.HTTPResponse(
        body.encode('utf-8'),
        headers,
        status,
        preload_content=False
    )


def mock_response(body, status):
    obj = http_mock_response(body, status)
    return rest.RESTResponse(obj, obj.data)


class TestOpenFgaClient(IsolatedAsyncioTestCase):
    """OpenFgaClient unit test stubs"""

    def setUp(self):
        self.client_configuration = openfga_sdk.ClientConfiguration(
            api_scheme='http',
            api_host="api.fga.example",
        )

    def tearDown(self):
        pass

    @patch.object(rest.RESTClientObject, 'request')
    async def test_check(self, mock_request):
        """Test case for check

        Check whether a user is authorized to access an object  # noqa: E501
        """

        # First, mock the response
        response_body = '{"allowed": true, "resolution": "1234"}'
        mock_request.return_value = mock_response(response_body, 200)

        configuration = self.client_configuration
        configuration.store_id = store_id
        async with openfga_sdk.ApiClient(configuration) as api_client:
            api_instance = open_fga_client.OpenFgaClient(api_client)
            body = ClientCheckRequest(
                user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                relation="reader",
                object="document:2021-budget",
            )
            options = ClientCheckRequestOpts(
                authorization_model_id="1uHxCSuTP0VKPYSnkq1pbb1jeZw"
            )
            api_response = await api_instance.check(
                body=body,
                options=options,
            )
            self.assertIsInstance(api_response, CheckResponse)
            self.assertTrue(api_response.allowed)
            # Make sure the API was called with the right data
            mock_request.assert_called_once_with(
                'POST',
                'http://api.fga.example/stores/d12345abc/check',
                headers=ANY,
                query_params=[],
                post_params=[],
                body={"tuple_key": {"object": "document:2021-budget",
                                    "relation": "reader", "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b"}, "authorization_model_id": "1uHxCSuTP0VKPYSnkq1pbb1jeZw"},
                _preload_content=ANY,
                _request_timeout=None
            )
            await api_client.close()
