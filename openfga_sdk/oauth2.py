import asyncio
import json
import math
import random
import sys

from datetime import datetime, timedelta

import urllib3

from openfga_sdk.configuration import Configuration
from openfga_sdk.constants import USER_AGENT
from openfga_sdk.credentials import Credentials
from openfga_sdk.exceptions import AuthenticationError
from openfga_sdk.telemetry.attributes import TelemetryAttributes
from openfga_sdk.telemetry.telemetry import Telemetry


def jitter(loop_count, min_wait_in_ms):
    """
    Generate a random jitter value for exponential backoff
    """
    minimum = math.ceil(2**loop_count * min_wait_in_ms)
    maximum = math.ceil(2 ** (loop_count + 1) * min_wait_in_ms)
    jitter = random.randrange(minimum, maximum) / 1000

    # If running in pytest, set jitter to 0 to speed up tests
    if "pytest" in sys.modules:
        jitter = 0

    return jitter


class OAuth2Client:
    def __init__(self, credentials: Credentials, configuration=None):
        self._credentials = credentials
        self._access_token = None
        self._access_expiry_time = None
        self._telemetry = Telemetry()

        if configuration is None:
            configuration = Configuration.get_default_copy()

        self.configuration = configuration

    def _token_valid(self):
        """
        Return whether token is valid
        """
        if self._access_token is None or self._access_expiry_time is None:
            return False
        if self._access_expiry_time < datetime.now():
            return False
        return True

    async def _obtain_token(self, client):
        """
        Perform OAuth2 and obtain token
        """
        configuration = self._credentials.configuration

        token_url = self._credentials._parse_issuer(configuration.api_issuer)

        post_params = {
            "client_id": configuration.client_id,
            "client_secret": configuration.client_secret,
            "audience": configuration.api_audience,
            "grant_type": "client_credentials",
        }

        # Add scope parameter if scopes are configured
        if configuration.scopes is not None:
            if isinstance(configuration.scopes, list):
                post_params["scope"] = " ".join(configuration.scopes)
            else:
                post_params["scope"] = configuration.scopes

        headers = urllib3.response.HTTPHeaderDict(
            {
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": USER_AGENT,
            }
        )

        max_retry = (
            self.configuration.retry_params.max_retry
            if (
                self.configuration.retry_params is not None
                and self.configuration.retry_params.max_retry is not None
            )
            else 0
        )

        min_wait_in_ms = (
            self.configuration.retry_params.min_wait_in_ms
            if (
                self.configuration.retry_params is not None
                and self.configuration.retry_params.min_wait_in_ms is not None
            )
            else 0
        )

        for attempt in range(max_retry + 1):
            raw_response = await client.request(
                method="POST",
                url=token_url,
                headers=headers,
                query_params=None,
                body=None,
                _preload_content=True,
                _request_timeout=None,
                post_params=post_params,
            )

            if 500 <= raw_response.status <= 599 or raw_response.status == 429:
                if attempt < max_retry and raw_response.status != 501:
                    await asyncio.sleep(jitter(attempt, min_wait_in_ms))
                    continue

            if 200 <= raw_response.status <= 299:
                try:
                    api_response = json.loads(raw_response.data)
                except Exception:
                    raise AuthenticationError(http_resp=raw_response)

                if api_response.get("expires_in") and api_response.get("access_token"):
                    self._access_expiry_time = datetime.now() + timedelta(
                        seconds=int(api_response.get("expires_in"))
                    )
                    self._access_token = api_response.get("access_token")
                    self._telemetry.metrics.credentialsRequest(
                        attributes={
                            TelemetryAttributes.fga_client_request_client_id: configuration.client_id
                        },
                        configuration=self.configuration.telemetry,
                    )
                    break

            raise AuthenticationError(http_resp=raw_response)

    async def get_authentication_header(self, client):
        """
        If configured, return the header for authentication
        """
        # check to see token is valid
        if not self._token_valid():
            # In this case, the token is not valid, we need to get the refresh the token
            await self._obtain_token(client)
        return {"Authorization": f"Bearer {self._access_token}"}
