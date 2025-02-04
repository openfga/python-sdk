import uuid

from unittest.mock import MagicMock

import pytest
import pytest_asyncio

from openfga_sdk.api.open_fga_api import OpenFgaApi
from openfga_sdk.client import OpenFgaClient
from openfga_sdk.factory import Factory
from openfga_sdk.models.authorization_model import AuthorizationModel
from openfga_sdk.models.create_store_response import CreateStoreResponse
from openfga_sdk.models.get_store_response import GetStoreResponse
from openfga_sdk.models.list_stores_response import ListStoresResponse
from openfga_sdk.models.read_authorization_model_response import (
    ReadAuthorizationModelResponse,
)
from openfga_sdk.models.read_authorization_models_response import (
    ReadAuthorizationModelsResponse,
)
from openfga_sdk.models.read_changes_response import ReadChangesResponse
from openfga_sdk.models.read_response import ReadResponse
from openfga_sdk.models.store import Store
from openfga_sdk.models.tuple import Tuple
from openfga_sdk.models.tuple_change import TupleChange
from openfga_sdk.models.write_authorization_model_response import (
    WriteAuthorizationModelResponse,
)
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
        stores=list(
            Store(
                **{
                    **store,
                    "created_at": parse_iso_datetime(store.get("created_at")),
                    "updated_at": parse_iso_datetime(store.get("updated_at")),
                    "deleted_at": parse_iso_datetime(store.get("deleted_at")),
                }
            )
            for store in mock_api_response_list_stores
        ),
        continuation_token=None,
    )


@pytest.fixture
def mock_api_response_create_store_deserialized(
    mock_api_response_create_store,
) -> CreateStoreResponse:
    return CreateStoreResponse(
        **{
            **mock_api_response_create_store,
            "created_at": parse_iso_datetime(
                mock_api_response_create_store["created_at"]
            ),
            "updated_at": parse_iso_datetime(
                mock_api_response_create_store["updated_at"]
            ),
        }
    )


@pytest.fixture
def mock_api_response_get_store_deserialized(
    mock_api_response_get_store,
) -> GetStoreResponse:
    return GetStoreResponse(
        **{
            **mock_api_response_get_store,
            "created_at": parse_iso_datetime(mock_api_response_get_store["created_at"]),
            "updated_at": parse_iso_datetime(mock_api_response_get_store["updated_at"]),
            "deleted_at": parse_iso_datetime(mock_api_response_get_store["deleted_at"]),
        }
    )


@pytest.fixture
def mock_api_response_read_authorization_model_deserialized(
    mock_api_response_read_authorization_model,
) -> ReadAuthorizationModelResponse:
    return ReadAuthorizationModelResponse(
        authorization_model=mock_api_response_read_authorization_model
    )


@pytest.fixture
def mock_api_response_read_authorization_models_deserialized(
    mock_api_response_read_authorization_models,
) -> ReadAuthorizationModelsResponse:
    return ReadAuthorizationModelsResponse(
        authorization_models=list(
            AuthorizationModel(
                **{
                    **model,
                }
            )
            for model in mock_api_response_read_authorization_models
        ),
    )


@pytest.fixture
def mock_api_continuation_token() -> str:
    return str(uuid.uuid4())


@pytest.fixture
def mock_api_response_write_authorization_model_deserialized(
    mock_api_response_write_authorization_model,
) -> WriteAuthorizationModelResponse:
    return WriteAuthorizationModelResponse(
        authorization_model_id=mock_api_response_write_authorization_model[
            "authorization_model_id"
        ]
    )


@pytest.fixture
def mock_api_response_read_changes_deserialized(
    mock_api_response_read_changes,
    mock_api_continuation_token,
) -> ReadChangesResponse:
    return ReadChangesResponse(
        changes=list(
            TupleChange(
                **{
                    **change,
                    "timestamp": parse_iso_datetime(change["timestamp"]),
                }
            )
            for change in mock_api_response_read_changes
        ),
        continuation_token=mock_api_continuation_token,
    )


@pytest.fixture
def mock_api_response_read_deserialized(
    mock_api_response_read,
    mock_api_continuation_token,
) -> ReadChangesResponse:
    return ReadResponse(
        tuples=list(
            Tuple(
                **{
                    **tuple,
                    "timestamp": parse_iso_datetime(tuple["timestamp"]),
                }
            )
            for tuple in mock_api_response_read
        ),
        continuation_token=mock_api_continuation_token,
    )
