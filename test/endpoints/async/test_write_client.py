"""
Python SDK for OpenFGA

API version: 1.x
Website: https://openfga.dev
Documentation: https://openfga.dev/docs
Support: https://openfga.dev/community
License: [Apache-2.0](https://github.com/openfga/python-sdk/blob/main/LICENSE)

NOTE: This file was auto generated by OpenAPI Generator (https://openapi-generator.tech). DO NOT EDIT.
"""

from unittest.mock import AsyncMock, patch

import pytest

from openfga_sdk.client.models.write_request import ClientWriteRequest
from openfga_sdk.client.models.write_response import ClientWriteResponse
from openfga_sdk.common.open_fga_api import ApiResponse
from openfga_sdk.common.options import DeleteStoreRequestOptions
from openfga_sdk.protocols import OpenFgaClientProtocol


@pytest.fixture
def api_request_response() -> ClientWriteResponse:
    return ClientWriteResponse()


@pytest.fixture
def api_request_conditions(
    api_request_response: ClientWriteResponse,
) -> dict[str, AsyncMock]:
    return {
        "attribute": "write",
        "new": AsyncMock(return_value=api_request_response),
    }


@pytest.mark.asyncio
class TestOpenFgaClientWriteStoreEndpoint:
    """
    @covers openfga_sdk.client.OpenFgaClient.write
    """

    async def test_write_issues_request(
        self,
        client: OpenFgaClientProtocol,
        api_request_conditions,
    ):
        """
        Test that the write method issues a request to OpenFgaApi.
        """
        with patch.object(client.api, **api_request_conditions) as api_request:
            await client.write(ClientWriteRequest())

            api_request.assert_called_once()

    async def test_write_returns_expected_response(
        self,
        client: OpenFgaClientProtocol,
        api_request_conditions,
    ):
        """
        Test that the write method returns the expected response.
        """
        with patch.object(client.api, **api_request_conditions):
            response = await client.write(ClientWriteRequest())

            assert isinstance(response, ClientWriteResponse)
