"""
Python SDK for OpenFGA

API version: 1.x
Website: https://openfga.dev
Documentation: https://openfga.dev/docs
Support: https://openfga.dev/community
License: [Apache-2.0](https://github.com/openfga/python-sdk/blob/main/LICENSE)

NOTE: This file was auto generated by OpenAPI Generator (https://openapi-generator.tech). DO NOT EDIT.
"""

import asyncio
import json

from dataclasses import dataclass
from datetime import datetime, timedelta

import urllib3

from openfga_sdk.common.headers import HttpHeader
from openfga_sdk.common.math import Math
from openfga_sdk.common.rest import RestClientProtocol
from openfga_sdk.exceptions import AuthenticationError
from openfga_sdk.protocols import (
    ConfigurationProtocol,
    HttpHeaderProtocol,
    OAuth2ClientProtocol,
)
from openfga_sdk.telemetry.attributes import TelemetryAttributes
from openfga_sdk.telemetry.telemetry import Telemetry


@dataclass
class OAuth2Client(OAuth2ClientProtocol):
    configuration: ConfigurationProtocol | None = None
    access_token: str | None = None
    access_expiry_time: datetime | None = None

    async def get_authentication_header(
        self,
        client: RestClientProtocol,
    ) -> HttpHeaderProtocol:
        """
        Get the authentication header for the client
        """

        if not self.token_valid():
            await self.obtain_token(client)

        return HttpHeader(name="Authorization", value=f"Bearer {self.access_token}")

    def token_valid(self) -> bool:
        """
        Return whether token is valid
        """

        if self.access_token is None or self.access_expiry_time is None:
            return False

        if self.access_expiry_time < datetime.now():
            return False

        return True

    async def obtain_token(
        self,
        client: RestClientProtocol,
    ) -> str:
        """
        Obtain a token from the OAuth2 server
        """

        if (
            self.configuration is None
            or self.configuration.credentials is None
            or self.configuration.credentials.configuration is None
        ):
            raise AuthenticationError("Credentials are not configured")

        if self.configuration.credentials.method != "client_credentials":
            raise AuthenticationError(
                f"Credentials method `{self.configuration.credentials.method}` is not supported"
            )

        token_url = f"https://{self.configuration.credentials.configuration.api_issuer}/oauth/token"

        post_params = {
            "client_id": self.configuration.credentials.configuration.client_id,
            "client_secret": self.configuration.credentials.configuration.client_secret,
            "audience": self.configuration.credentials.configuration.api_audience,
            "grant_type": "client_credentials",
        }

        headers = urllib3.response.HTTPHeaderDict(
            {
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "openfga-sdk (python) 0.9.1",
            }
        )

        for attempt in range(self.configuration.retry_params.max_retries + 1):
            response = await client.request(
                method="POST",
                url=token_url,
                headers=headers,
                post_params=post_params,
            )

            if 500 <= response.status <= 599 or response.status == 429:
                if (
                    attempt < self.configuration.retry_params.max_retries
                    and response.status != 501
                ):
                    await asyncio.sleep(
                        Math.jitter(
                            attempt, self.configuration.retry_params.min_wait_in_ms
                        )
                    )

                    continue

            if type(response.data) in [bytes, str] and 200 <= response.status <= 299:
                try:
                    api_response = json.loads(response.data)
                except Exception:
                    raise AuthenticationError(http_resp=response)

                expires_in = api_response.get("expires_in")
                access_token = api_response.get("access_token")

                if (
                    type(expires_in) is int
                    and type(access_token) is str
                    and self.configuration.credentials.configuration.client_id
                    is not None
                ):
                    Telemetry().metrics.credentialsRequest(
                        attributes={
                            TelemetryAttributes.fga_client_request_client_id: self.configuration.credentials.configuration.client_id
                        },
                        configuration=self.configuration.telemetry,
                    )

                    self.access_expiry_time = datetime.now() + timedelta(
                        seconds=int(expires_in)
                    )

                    self.access_token = access_token

                    return self.access_token

            raise AuthenticationError(http_resp=response)
