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

from openfga_sdk.common.open_fga_api import ApiResponse
from openfga_sdk.common.options import ListStoresRequestOptions
from openfga_sdk.models.list_stores_response import ListStoresResponse
from openfga_sdk.protocols import ApiResponseProtocol, OpenFgaClientProtocol


@pytest.fixture
def api_request_response(
    mock_api_response_list_stores_deserialized: ListStoresResponse,
) -> ApiResponseProtocol:
    return ApiResponse(
        deserialized=mock_api_response_list_stores_deserialized,
    )


@pytest.fixture
def api_request_conditions(
    api_request_response: ApiResponse,
):
    return {
        "attribute": "list_stores",
        "new": AsyncMock(return_value=api_request_response),
    }


@pytest.mark.asyncio
class TestOpenFgaClientListStoresEndpoint:
    """
    @covers openfga_sdk.client.OpenFgaClient.list_stores
    """

    async def test_list_stores_issues_request(
        self,
        client: OpenFgaClientProtocol,
        api_request_conditions,
    ):
        """
        Test that the list_stores method issues a request to OpenFgaApi.
        """
        with patch.object(client.api, **api_request_conditions) as api_request:
            await client.list_stores()

            api_request.assert_called_once()

    async def test_list_stores_returns_expected_response(
        self,
        client: OpenFgaClientProtocol,
        mock_api_response_list_stores_deserialized: ListStoresResponse,
        api_request_conditions,
    ):
        """
        Test that the list_stores method returns a ListStoresResponse instance containing the expected response.
        """
        with patch.object(client.api, **api_request_conditions):
            response = await client.list_stores()

            assert response == mock_api_response_list_stores_deserialized

    async def test_list_stores_returns_full_response(
        self,
        client: OpenFgaClientProtocol,
        api_request_response: ApiResponse,
        api_request_conditions,
    ):
        """
        Test that the list_stores method returns an ApiResponse instance containing the expected response.
        """
        options = ListStoresRequestOptions(
            return_response=True,
        )

        with patch.object(client.api, **api_request_conditions):
            response = await client.list_stores(options)

            assert response == api_request_response
