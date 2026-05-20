import asyncio

from datetime import datetime, timedelta
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch

import urllib3

from openfga_sdk import rest
from openfga_sdk._version import USER_AGENT
from openfga_sdk.configuration import Configuration
from openfga_sdk.constants import TOKEN_EXPIRY_THRESHOLD_BUFFER_IN_SEC
from openfga_sdk.credentials import CredentialConfiguration, Credentials
from openfga_sdk.exceptions import AuthenticationError
from openfga_sdk.oauth2 import OAuth2Client
from openfga_sdk.oauth2_common import _TokenState


# Helper function to construct mock response
def mock_response(body, status):
    headers = urllib3.response.HTTPHeaderDict({"content-type": "application/json"})
    obj = urllib3.HTTPResponse(body, headers, status, preload_content=False)
    return rest.RESTResponse(obj, obj.data)


class TestOAuth2Client(IsolatedAsyncioTestCase):
    """TestOAuth2Client unit test"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    async def test_get_authentication_valid_client_credentials(self):
        """
        Test getting authentication header when method is client credentials
        """
        client = OAuth2Client(None)
        client._token_state = _TokenState(
            access_token="XYZ123",
            expiry_time=datetime.now() + timedelta(seconds=3600),
            expiry_buffer=0,
        )
        auth_header = await client.get_authentication_header(None)
        self.assertEqual(auth_header, {"Authorization": "Bearer XYZ123"})

    @patch.object(rest.RESTClientObject, "request")
    async def test_get_authentication_obtain_client_credentials(self, mock_request):
        """
        Test getting authentication header when method is client credential and we need to obtain token
        """
        response_body = """
{
  "expires_in": 120,
  "access_token": "AABBCCDD"
}
        """
        mock_request.return_value = mock_response(response_body, 200)

        credentials = Credentials(
            method="client_credentials",
            configuration=CredentialConfiguration(
                client_id="myclientid",
                client_secret="mysecret",
                api_issuer="issuer.fga.example",
                api_audience="myaudience",
            ),
        )
        rest_client = rest.RESTClientObject(Configuration())
        current_time = datetime.now()
        client = OAuth2Client(credentials)
        auth_header = await client.get_authentication_header(rest_client)
        self.assertEqual(auth_header, {"Authorization": "Bearer AABBCCDD"})
        self.assertEqual(client._token_state.access_token, "AABBCCDD")
        self.assertGreaterEqual(
            client._token_state.expiry_time, current_time + timedelta(seconds=120)
        )
        expected_header = urllib3.response.HTTPHeaderDict(
            {
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": USER_AGENT,
            }
        )
        mock_request.assert_called_once_with(
            method="POST",
            url="https://issuer.fga.example/oauth/token",
            headers=expected_header,
            query_params=None,
            body=None,
            _preload_content=True,
            _request_timeout=None,
            post_params={
                "client_id": "myclientid",
                "client_secret": "mysecret",
                "audience": "myaudience",
                "grant_type": "client_credentials",
            },
        )
        await rest_client.close()

    @patch.object(rest.RESTClientObject, "request")
    async def test_get_authentication_obtain_client_credentials_failed(
        self, mock_request
    ):
        """
        Test getting authentication header when method is client credential and we fail to obtain token
        """
        response_body = """
{
  "reason": "Unauthorized"
}
        """
        mock_request.return_value = mock_response(response_body, 403)

        credentials = Credentials(
            method="client_credentials",
            configuration=CredentialConfiguration(
                client_id="myclientid",
                client_secret="mysecret",
                api_issuer="issuer.fga.example",
                api_audience="myaudience",
            ),
        )
        rest_client = rest.RESTClientObject(Configuration())
        client = OAuth2Client(credentials)
        with self.assertRaises(AuthenticationError):
            await client.get_authentication_header(rest_client)
        await rest_client.close()

    @patch.object(rest.RESTClientObject, "request")
    async def test_get_authentication_obtain_with_expired_client_credentials_failed(
        self, mock_request
    ):
        """
        Expired token should trigger a new token request
        """

        response_body = """
{
  "reason": "Unauthorized"
}
        """
        mock_request.return_value = mock_response(response_body, 403)

        credentials = Credentials(
            method="client_credentials",
            configuration=CredentialConfiguration(
                client_id="myclientid",
                client_secret="mysecret",
                api_issuer="issuer.fga.example",
                api_audience="myaudience",
            ),
        )
        rest_client = rest.RESTClientObject(Configuration())
        client = OAuth2Client(credentials)

        client._token_state = _TokenState(
            access_token="XYZ123",
            expiry_time=datetime.now() - timedelta(seconds=240),
            expiry_buffer=0,
        )

        with self.assertRaises(AuthenticationError):
            await client.get_authentication_header(rest_client)
        await rest_client.close()

    @patch.object(rest.RESTClientObject, "request")
    async def test_get_authentication_unexpected_response_fails(self, mock_request):
        """
        Receiving an unexpected response from the server should raise an exception
        """

        response_body = """
This is not a JSON response
        """
        mock_request.return_value = mock_response(response_body, 200)

        credentials = Credentials(
            method="client_credentials",
            configuration=CredentialConfiguration(
                client_id="myclientid",
                client_secret="mysecret",
                api_issuer="issuer.fga.example",
                api_audience="myaudience",
            ),
        )
        rest_client = rest.RESTClientObject(Configuration())
        client = OAuth2Client(credentials)

        with self.assertRaises(AuthenticationError):
            await client.get_authentication_header(rest_client)
        await rest_client.close()

    @patch.object(rest.RESTClientObject, "request")
    async def test_get_authentication_erroneous_response_fails(self, mock_request):
        """
        Receiving an erroneous response from the server that's missing properties should raise an exception
        """

        response_body = """
{
  "access_token": "AABBCCDD"
}
        """
        mock_request.return_value = mock_response(response_body, 200)

        credentials = Credentials(
            method="client_credentials",
            configuration=CredentialConfiguration(
                client_id="myclientid",
                client_secret="mysecret",
                api_issuer="issuer.fga.example",
                api_audience="myaudience",
            ),
        )
        rest_client = rest.RESTClientObject(Configuration())
        client = OAuth2Client(credentials)

        with self.assertRaises(AuthenticationError):
            await client.get_authentication_header(rest_client)
        await rest_client.close()

    @patch.object(rest.RESTClientObject, "request")
    async def test_get_authentication_retries_5xx_responses(self, mock_request):
        """
        Receiving a 5xx response from the server should be retried
        """

        error_response_body = """
{
  "code": "rate_limit_exceeded",
  "message": "Rate Limit exceeded"
}
        """

        response_body = """
{
  "expires_in": 120,
  "access_token": "AABBCCDD"
}
        """

        mock_request.side_effect = [
            mock_response(error_response_body, 429),
            mock_response(error_response_body, 429),
            mock_response(error_response_body, 429),
            mock_response(response_body, 200),
        ]

        credentials = Credentials(
            method="client_credentials",
            configuration=CredentialConfiguration(
                client_id="myclientid",
                client_secret="mysecret",
                api_issuer="issuer.fga.example",
                api_audience="myaudience",
            ),
        )

        configuration = Configuration()
        configuration.retry_params.max_retry = 5
        configuration.retry_params.retry_interval = 0

        rest_client = rest.RESTClientObject(configuration)
        client = OAuth2Client(credentials, configuration)

        auth_header = await client.get_authentication_header(rest_client)

        mock_request.assert_called()
        self.assertEqual(mock_request.call_count, 4)  # 3 retries, 1 success
        self.assertEqual(auth_header, {"Authorization": "Bearer AABBCCDD"})

        await rest_client.close()

    @patch.object(rest.RESTClientObject, "request")
    async def test_get_authentication_keep_full_url(self, mock_request):
        """
        Fully qualified issuer URLs should not get manipulated.
        """
        response_body = """
{
  "expires_in": 120,
  "access_token": "AABBCCDD"
}
        """
        mock_request.return_value = mock_response(response_body, 200)

        credentials = Credentials(
            method="client_credentials",
            configuration=CredentialConfiguration(
                client_id="myclientid",
                client_secret="mysecret",
                api_issuer="https://issuer.fga.example/something",
                api_audience="myaudience",
            ),
        )
        rest_client = rest.RESTClientObject(Configuration())
        current_time = datetime.now()
        client = OAuth2Client(credentials)
        auth_header = await client.get_authentication_header(rest_client)
        self.assertEqual(auth_header, {"Authorization": "Bearer AABBCCDD"})
        self.assertEqual(client._token_state.access_token, "AABBCCDD")
        self.assertGreaterEqual(
            client._token_state.expiry_time, current_time + timedelta(seconds=120)
        )
        expected_header = urllib3.response.HTTPHeaderDict(
            {
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": USER_AGENT,
            }
        )
        mock_request.assert_called_once_with(
            method="POST",
            url="https://issuer.fga.example/something",
            headers=expected_header,
            query_params=None,
            body=None,
            _preload_content=True,
            _request_timeout=None,
            post_params={
                "client_id": "myclientid",
                "client_secret": "mysecret",
                "audience": "myaudience",
                "grant_type": "client_credentials",
            },
        )
        await rest_client.close()

    @patch.object(rest.RESTClientObject, "request")
    async def test_get_authentication_add_scheme(self, mock_request):
        """
        Issuer URLs without scheme should get scheme prefix added.
        """
        response_body = """
{
  "expires_in": 120,
  "access_token": "AABBCCDD"
}
        """
        mock_request.return_value = mock_response(response_body, 200)

        credentials = Credentials(
            method="client_credentials",
            configuration=CredentialConfiguration(
                client_id="myclientid",
                client_secret="mysecret",
                api_issuer="issuer.fga.example/something",
                api_audience="myaudience",
            ),
        )
        rest_client = rest.RESTClientObject(Configuration())
        current_time = datetime.now()
        client = OAuth2Client(credentials)
        auth_header = await client.get_authentication_header(rest_client)
        self.assertEqual(auth_header, {"Authorization": "Bearer AABBCCDD"})
        self.assertEqual(client._token_state.access_token, "AABBCCDD")
        self.assertGreaterEqual(
            client._token_state.expiry_time, current_time + timedelta(seconds=120)
        )
        expected_header = urllib3.response.HTTPHeaderDict(
            {
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": USER_AGENT,
            }
        )
        mock_request.assert_called_once_with(
            method="POST",
            url="https://issuer.fga.example/something",
            headers=expected_header,
            query_params=None,
            body=None,
            _preload_content=True,
            _request_timeout=None,
            post_params={
                "client_id": "myclientid",
                "client_secret": "mysecret",
                "audience": "myaudience",
                "grant_type": "client_credentials",
            },
        )
        await rest_client.close()

    @patch.object(rest.RESTClientObject, "request")
    async def test_get_authentication_add_path(self, mock_request):
        """
        Issuer URLs without scheme should get scheme prefix added.
        """
        response_body = """
{
  "expires_in": 120,
  "access_token": "AABBCCDD"
}
        """
        mock_request.return_value = mock_response(response_body, 200)

        credentials = Credentials(
            method="client_credentials",
            configuration=CredentialConfiguration(
                client_id="myclientid",
                client_secret="mysecret",
                api_issuer="https://issuer.fga.example",
                api_audience="myaudience",
            ),
        )
        rest_client = rest.RESTClientObject(Configuration())
        current_time = datetime.now()
        client = OAuth2Client(credentials)
        auth_header = await client.get_authentication_header(rest_client)
        self.assertEqual(auth_header, {"Authorization": "Bearer AABBCCDD"})
        self.assertEqual(client._token_state.access_token, "AABBCCDD")
        self.assertGreaterEqual(
            client._token_state.expiry_time, current_time + timedelta(seconds=120)
        )
        expected_header = urllib3.response.HTTPHeaderDict(
            {
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": USER_AGENT,
            }
        )
        mock_request.assert_called_once_with(
            method="POST",
            url="https://issuer.fga.example/oauth/token",
            headers=expected_header,
            query_params=None,
            body=None,
            _preload_content=True,
            _request_timeout=None,
            post_params={
                "client_id": "myclientid",
                "client_secret": "mysecret",
                "audience": "myaudience",
                "grant_type": "client_credentials",
            },
        )
        await rest_client.close()

    @patch.object(rest.RESTClientObject, "request")
    async def test_get_authentication_add_scheme_and_path(self, mock_request):
        """
        Issuer URLs without scheme should get scheme prefix added.
        """
        response_body = """
{
  "expires_in": 120,
  "access_token": "AABBCCDD"
}
        """
        mock_request.return_value = mock_response(response_body, 200)

        credentials = Credentials(
            method="client_credentials",
            configuration=CredentialConfiguration(
                client_id="myclientid",
                client_secret="mysecret",
                api_issuer="issuer.fga.example",
                api_audience="myaudience",
            ),
        )
        rest_client = rest.RESTClientObject(Configuration())
        current_time = datetime.now()
        client = OAuth2Client(credentials)
        auth_header = await client.get_authentication_header(rest_client)
        self.assertEqual(auth_header, {"Authorization": "Bearer AABBCCDD"})
        self.assertEqual(client._token_state.access_token, "AABBCCDD")
        self.assertGreaterEqual(
            client._token_state.expiry_time, current_time + timedelta(seconds=120)
        )
        expected_header = urllib3.response.HTTPHeaderDict(
            {
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": USER_AGENT,
            }
        )
        mock_request.assert_called_once_with(
            method="POST",
            url="https://issuer.fga.example/oauth/token",
            headers=expected_header,
            query_params=None,
            body=None,
            _preload_content=True,
            _request_timeout=None,
            post_params={
                "client_id": "myclientid",
                "client_secret": "mysecret",
                "audience": "myaudience",
                "grant_type": "client_credentials",
            },
        )
        await rest_client.close()

    @patch.object(rest.RESTClientObject, "request")
    async def test_get_authentication_obtain_client_credentials_with_scopes_list(
        self, mock_request
    ):
        """
        Test getting authentication header when method is client credentials with scopes as list
        """
        response_body = """
{
  "expires_in": 120,
  "access_token": "AABBCCDD"
}
        """
        mock_request.return_value = mock_response(response_body, 200)

        credentials = Credentials(
            method="client_credentials",
            configuration=CredentialConfiguration(
                client_id="myclientid",
                client_secret="mysecret",
                api_issuer="issuer.fga.example",
                api_audience="myaudience",
                scopes=["read", "write", "admin"],
            ),
        )
        rest_client = rest.RESTClientObject(Configuration())
        current_time = datetime.now()
        client = OAuth2Client(credentials)
        auth_header = await client.get_authentication_header(rest_client)
        self.assertEqual(auth_header, {"Authorization": "Bearer AABBCCDD"})
        self.assertEqual(client._token_state.access_token, "AABBCCDD")
        self.assertGreaterEqual(
            client._token_state.expiry_time, current_time + timedelta(seconds=120)
        )
        expected_header = urllib3.response.HTTPHeaderDict(
            {
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": USER_AGENT,
            }
        )
        mock_request.assert_called_once_with(
            method="POST",
            url="https://issuer.fga.example/oauth/token",
            headers=expected_header,
            query_params=None,
            body=None,
            _preload_content=True,
            _request_timeout=None,
            post_params={
                "client_id": "myclientid",
                "client_secret": "mysecret",
                "audience": "myaudience",
                "grant_type": "client_credentials",
                "scope": "read write admin",
            },
        )
        await rest_client.close()

    @patch.object(rest.RESTClientObject, "request")
    async def test_get_authentication_obtain_client_credentials_with_scopes_string(
        self, mock_request
    ):
        """
        Test getting authentication header when method is client credentials with scopes as string
        """
        response_body = """
{
  "expires_in": 120,
  "access_token": "AABBCCDD"
}
        """
        mock_request.return_value = mock_response(response_body, 200)

        credentials = Credentials(
            method="client_credentials",
            configuration=CredentialConfiguration(
                client_id="myclientid",
                client_secret="mysecret",
                api_issuer="issuer.fga.example",
                api_audience="myaudience",
                scopes="read write admin",
            ),
        )
        rest_client = rest.RESTClientObject(Configuration())
        current_time = datetime.now()
        client = OAuth2Client(credentials)
        auth_header = await client.get_authentication_header(rest_client)
        self.assertEqual(auth_header, {"Authorization": "Bearer AABBCCDD"})
        self.assertEqual(client._token_state.access_token, "AABBCCDD")
        self.assertGreaterEqual(
            client._token_state.expiry_time, current_time + timedelta(seconds=120)
        )
        expected_header = urllib3.response.HTTPHeaderDict(
            {
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": USER_AGENT,
            }
        )
        mock_request.assert_called_once_with(
            method="POST",
            url="https://issuer.fga.example/oauth/token",
            headers=expected_header,
            query_params=None,
            body=None,
            _preload_content=True,
            _request_timeout=None,
            post_params={
                "client_id": "myclientid",
                "client_secret": "mysecret",
                "audience": "myaudience",
                "grant_type": "client_credentials",
                "scope": "read write admin",
            },
        )
        await rest_client.close()

    @patch.object(rest.RESTClientObject, "request")
    async def test_get_authentication_without_audience(self, mock_request):
        """
        Test that audience is omitted from the token request when not provided
        (standard OAuth2 flow without Auth0 audience extension)
        """
        response_body = """
{
  "expires_in": 120,
  "access_token": "AABBCCDD"
}
        """
        mock_request.return_value = mock_response(response_body, 200)

        credentials = Credentials(
            method="client_credentials",
            configuration=CredentialConfiguration(
                client_id="myclientid",
                client_secret="mysecret",
                api_issuer="issuer.fga.example",
            ),
        )
        rest_client = rest.RESTClientObject(Configuration())
        client = OAuth2Client(credentials)
        auth_header = await client.get_authentication_header(rest_client)
        self.assertEqual(auth_header, {"Authorization": "Bearer AABBCCDD"})
        expected_header = urllib3.response.HTTPHeaderDict(
            {
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": USER_AGENT,
            }
        )
        mock_request.assert_called_once_with(
            method="POST",
            url="https://issuer.fga.example/oauth/token",
            headers=expected_header,
            query_params=None,
            body=None,
            _preload_content=True,
            _request_timeout=None,
            post_params={
                "client_id": "myclientid",
                "client_secret": "mysecret",
                "grant_type": "client_credentials",
            },
        )
        await rest_client.close()

    @patch.object(rest.RESTClientObject, "request")
    @patch("openfga_sdk.oauth2.random")
    async def test_get_authentication_refreshes_near_expiry_token(
        self, mock_random, mock_request
    ):
        """
        Token close to expiry (within buffer window) should trigger a proactive refresh
        """
        mock_random.random.return_value = 0
        short_lived_secs = max(1, TOKEN_EXPIRY_THRESHOLD_BUFFER_IN_SEC - 1)

        mock_request.side_effect = [
            mock_response(
                f'{{"expires_in": {short_lived_secs}, "access_token": "short-lived-token"}}',
                200,
            ),
            mock_response(
                '{"expires_in": 3600, "access_token": "refreshed-token"}',
                200,
            ),
        ]

        credentials = Credentials(
            method="client_credentials",
            configuration=CredentialConfiguration(
                client_id="myclientid",
                client_secret="mysecret",
                api_issuer="issuer.fga.example",
                api_audience="myaudience",
            ),
        )
        rest_client = rest.RESTClientObject(Configuration())
        client = OAuth2Client(credentials)

        header1 = await client.get_authentication_header(rest_client)
        header2 = await client.get_authentication_header(rest_client)

        self.assertEqual(header1, {"Authorization": "Bearer short-lived-token"})
        self.assertEqual(header2, {"Authorization": "Bearer refreshed-token"})
        self.assertEqual(mock_request.call_count, 2)

        await rest_client.close()

    async def test_concurrent_requests_only_fetch_token_once(self):
        """
        Multiple concurrent requests while the token is invalid should result in
        only one token fetch — subsequent coroutines wait on the lock and reuse
        the token obtained by the first.
        """
        obtain_calls = []

        credentials = Credentials(
            method="client_credentials",
            configuration=CredentialConfiguration(
                client_id="myclientid",
                client_secret="mysecret",
                api_issuer="issuer.fga.example",
                api_audience="myaudience",
            ),
        )
        oauth_client = OAuth2Client(credentials)

        async def mock_obtain_token(client):
            obtain_calls.append(1)
            await asyncio.sleep(0)  # yield so other coroutines reach the lock
            oauth_client._token_state = _TokenState(
                access_token="concurrent-token",
                expiry_time=datetime.now() + timedelta(seconds=3600),
                expiry_buffer=300,
            )

        with patch.object(oauth_client, "_obtain_token", side_effect=mock_obtain_token):
            results = await asyncio.gather(
                *[oauth_client.get_authentication_header(None) for _ in range(5)]
            )

        self.assertEqual(len(obtain_calls), 1)
        self.assertTrue(
            all(r == {"Authorization": "Bearer concurrent-token"} for r in results)
        )

    @patch.object(rest.RESTClientObject, "request")
    async def test_get_authentication_with_scopes_no_audience(self, mock_request):
        """
        Test that scope is sent and audience is omitted when only scopes are provided
        (standard OAuth2 flow)
        """
        response_body = """
{
  "expires_in": 120,
  "access_token": "AABBCCDD"
}
        """
        mock_request.return_value = mock_response(response_body, 200)

        credentials = Credentials(
            method="client_credentials",
            configuration=CredentialConfiguration(
                client_id="myclientid",
                client_secret="mysecret",
                api_issuer="issuer.fga.example",
                scopes="read write",
            ),
        )
        rest_client = rest.RESTClientObject(Configuration())
        client = OAuth2Client(credentials)
        auth_header = await client.get_authentication_header(rest_client)
        self.assertEqual(auth_header, {"Authorization": "Bearer AABBCCDD"})
        expected_header = urllib3.response.HTTPHeaderDict(
            {
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": USER_AGENT,
            }
        )
        mock_request.assert_called_once_with(
            method="POST",
            url="https://issuer.fga.example/oauth/token",
            headers=expected_header,
            query_params=None,
            body=None,
            _preload_content=True,
            _request_timeout=None,
            post_params={
                "client_id": "myclientid",
                "client_secret": "mysecret",
                "grant_type": "client_credentials",
                "scope": "read write",
            },
        )
        await rest_client.close()
