from openfga_sdk.models.store import Store
import pytest
import pytest_asyncio

from unittest.mock import MagicMock

from openfga_sdk.api.open_fga_api import OpenFgaApi
from openfga_sdk.client import OpenFgaClient
from openfga_sdk.factory import Factory
from openfga_sdk.models.list_stores_response import ListStoresResponse
from openfga_sdk.protocols import ConfigurationProtocol, FactoryProtocol
from test.conftest import parse_iso_datetime


@pytest.fixture
def mock_configuration_api_url() -> str:
    return "https://api.fga.example"


@pytest.fixture
def mock_configuration(mock_configuration_api_url: str) -> ConfigurationProtocol:
    configuration = MagicMock()
    configuration.api_url = mock_configuration_api_url

    return configuration


@pytest_asyncio.fixture
async def factory(
    mock_configuration: ConfigurationProtocol,
):
    yield Factory(
        configuration=mock_configuration,
    )


@pytest_asyncio.fixture
async def client(
    mock_configuration: ConfigurationProtocol,
    factory: FactoryProtocol,
):
    client = OpenFgaClient(
        configuration=mock_configuration,
        factory=factory,
    )
    yield client
    await client.close()


@pytest_asyncio.fixture
async def api(
    mock_configuration: ConfigurationProtocol,
    factory: FactoryProtocol,
):
    api = OpenFgaApi(
        configuration=mock_configuration,
        factory=factory,
    )
    yield api
    await api.close()


@pytest.fixture
def mock_api_response_list_stores_deserialized(
    mock_api_response_list_stores,
) -> ListStoresResponse:
    return ListStoresResponse(
        stores=[
            Store(
                **{
                    **store,
                    "created_at": parse_iso_datetime(store.get("created_at")),
                    "updated_at": parse_iso_datetime(store.get("updated_at")),
                    "deleted_at": parse_iso_datetime(store.get("deleted_at")),
                }
            )
            for store in mock_api_response_list_stores
        ],
    )
