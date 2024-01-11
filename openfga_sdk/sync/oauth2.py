"""
   Python SDK for OpenFGA

   API version: 0.1
   Website: https://openfga.dev
   Documentation: https://openfga.dev/docs
   Support: https://discord.gg/8naAwJfWN6
   License: [Apache-2.0](https://github.com/openfga/python-sdk/blob/main/LICENSE)

   NOTE: This file was auto generated by OpenAPI Generator (https://openapi-generator.tech). DO NOT EDIT.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import typing
import urllib3
from urllib.parse import urlparse

from openfga_sdk.credentials import Credentials
from openfga_sdk.exceptions import AuthenticationError


class OAuth2Client:

    def __init__(
        self,
        credentials: Credentials
    ):
        self._credentials = credentials
        self._access_token = None
        self._access_expiry_time = None

    def _token_valid(self):
        """
        Return whether token is valid
        """
        if self._access_token is None or self._access_expiry_time is None:
            return False
        if self._access_expiry_time < datetime.now():
            return False
        return True

    def _obtain_token(self, client):
        """
        Perform OAuth2 and obtain token
        """
        configuration = self._credentials.configuration
        token_url = 'https://{}/oauth/token'.format(configuration.api_issuer)
        body = {
            'client_id': configuration.client_id,
            'client_secret': configuration.client_secret,
            'audience': configuration.api_audience,
            'grant_type': "client_credentials",
        }
        headers = urllib3.response.HTTPHeaderDict(
            {'Accept': 'application/json', 'Content-Type': 'application/json', 'User-Agent': 'openfga-sdk (python) 0.4.0'})
        raw_response = client.POST(token_url, headers=headers, body=body)
        if 200 <= raw_response.status <= 299:
            try:
                api_response = json.loads(raw_response.data)
            except:  # noqa: E722
                raise AuthenticationError(http_resp=raw_response)
            if not api_response.get('expires_in') or not api_response.get('access_token'):
                raise AuthenticationError(http_resp=raw_response)
            self._access_expiry_time = datetime.now() + timedelta(seconds=int(api_response.get('expires_in')))
            self._access_token = api_response.get('access_token')
        else:
            raise AuthenticationError(http_resp=raw_response)

    def get_authentication_header(self, client):
        """
        If configured, return the header for authentication
        """
        # check to see token is valid
        if not self._token_valid():
            # In this case, the token is not valid, we need to get the refresh the token
            self._obtain_token(client)
        return {'Authorization': 'Bearer {}'.format(self._access_token)}
