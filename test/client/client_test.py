import copy
import json
import uuid

from datetime import datetime
from unittest import IsolatedAsyncioTestCase
from unittest.mock import ANY, patch

import pytest
import urllib3

from openfga_sdk import rest
from openfga_sdk.client import ClientConfiguration
from openfga_sdk.client.client import OpenFgaClient, set_heading_if_not_set
from openfga_sdk.client.models.assertion import ClientAssertion
from openfga_sdk.client.models.batch_check_item import ClientBatchCheckItem
from openfga_sdk.client.models.batch_check_request import ClientBatchCheckRequest
from openfga_sdk.client.models.check_request import ClientCheckRequest
from openfga_sdk.client.models.expand_request import ClientExpandRequest
from openfga_sdk.client.models.list_objects_request import ClientListObjectsRequest
from openfga_sdk.client.models.list_relations_request import ClientListRelationsRequest
from openfga_sdk.client.models.list_users_request import ClientListUsersRequest
from openfga_sdk.client.models.read_changes_request import ClientReadChangesRequest
from openfga_sdk.client.models.tuple import ClientTuple
from openfga_sdk.client.models.write_request import ClientWriteRequest
from openfga_sdk.client.models.write_single_response import ClientWriteSingleResponse
from openfga_sdk.client.models.write_transaction_opts import WriteTransactionOpts
from openfga_sdk.configuration import RetryParams
from openfga_sdk.exceptions import (
    FgaValidationException,
    UnauthorizedException,
    ValidationException,
)
from openfga_sdk.models.assertion import Assertion
from openfga_sdk.models.authorization_model import AuthorizationModel
from openfga_sdk.models.check_response import CheckResponse
from openfga_sdk.models.consistency_preference import ConsistencyPreference
from openfga_sdk.models.create_store_request import CreateStoreRequest
from openfga_sdk.models.create_store_response import CreateStoreResponse
from openfga_sdk.models.expand_response import ExpandResponse
from openfga_sdk.models.fga_object import FgaObject
from openfga_sdk.models.get_store_response import GetStoreResponse
from openfga_sdk.models.leaf import Leaf
from openfga_sdk.models.list_objects_response import ListObjectsResponse
from openfga_sdk.models.list_stores_response import ListStoresResponse
from openfga_sdk.models.list_users_response import ListUsersResponse
from openfga_sdk.models.node import Node
from openfga_sdk.models.object_relation import ObjectRelation
from openfga_sdk.models.read_assertions_response import ReadAssertionsResponse
from openfga_sdk.models.read_authorization_model_response import (
    ReadAuthorizationModelResponse,
)
from openfga_sdk.models.read_authorization_models_response import (
    ReadAuthorizationModelsResponse,
)
from openfga_sdk.models.read_changes_response import ReadChangesResponse
from openfga_sdk.models.read_request_tuple_key import ReadRequestTupleKey
from openfga_sdk.models.read_response import ReadResponse
from openfga_sdk.models.store import Store
from openfga_sdk.models.tuple import Tuple
from openfga_sdk.models.tuple_change import TupleChange
from openfga_sdk.models.tuple_key import TupleKey
from openfga_sdk.models.tuple_key_without_condition import TupleKeyWithoutCondition
from openfga_sdk.models.tuple_operation import TupleOperation
from openfga_sdk.models.type_definition import TypeDefinition
from openfga_sdk.models.user_type_filter import UserTypeFilter
from openfga_sdk.models.users import Users
from openfga_sdk.models.userset import Userset
from openfga_sdk.models.userset_tree import UsersetTree
from openfga_sdk.models.usersets import Usersets
from openfga_sdk.models.validation_error_message_response import (
    ValidationErrorMessageResponse,
)
from openfga_sdk.models.write_authorization_model_request import (
    WriteAuthorizationModelRequest,
)
from openfga_sdk.models.write_authorization_model_response import (
    WriteAuthorizationModelResponse,
)


store_id = "01YCP46JKYM8FJCQ37NMBYHE5X"
request_id = "x1y2z3"


# Helper function to construct mock response
def http_mock_response(body, status):
    headers = urllib3.response.HTTPHeaderDict(
        {"content-type": "application/json", "Fga-Request-Id": request_id}
    )
    return urllib3.HTTPResponse(
        body.encode("utf-8"), headers, status, preload_content=False
    )


def mock_response(body, status):
    obj = http_mock_response(body, status)
    return rest.RESTResponse(obj, obj.data)


class TestOpenFgaClient(IsolatedAsyncioTestCase):
    """Test for OpenFGA Client"""

    def setUp(self):
        self.configuration = ClientConfiguration(
            api_url="http://api.fga.example",
        )

    def tearDown(self):
        pass

    @patch.object(rest.RESTClientObject, "request")
    async def test_list_stores(self, mock_request):
        """Test case for list_stores

        Get all stores
        """
        response_body = """
{
  "stores": [
    {
      "id": "01YCP46JKYM8FJCQ37NMBYHE5X",
      "name": "store1",
      "created_at": "2022-07-25T21:15:37.524Z",
      "updated_at": "2022-07-25T21:15:37.524Z",
      "deleted_at": "2022-07-25T21:15:37.524Z"
    },
    {
      "id": "01YCP46JKYM8FJCQ37NMBYHE6X",
      "name": "store2",
      "created_at": "2022-07-25T21:15:37.524Z",
      "updated_at": "2022-07-25T21:15:37.524Z",
      "deleted_at": "2022-07-25T21:15:37.524Z"
    }
  ],
  "continuation_token": "eyJwayI6IkxBVEVTVF9OU0NPTkZJR19hdXRoMHN0b3JlIiwic2siOiIxem1qbXF3MWZLZExTcUoyN01MdTdqTjh0cWgifQ=="
}
            """
        mock_request.return_value = mock_response(response_body, 200)
        configuration = self.configuration
        async with OpenFgaClient(configuration) as api_client:
            api_response = await api_client.list_stores(
                options={
                    "page_size": 1,
                    "continuation_token": "continuation_token_example",
                }
            )
            self.assertIsInstance(api_response, ListStoresResponse)
            self.assertEqual(
                api_response.continuation_token,
                "eyJwayI6IkxBVEVTVF9OU0NPTkZJR19hdXRoMHN0b3JlIiwic2siOiIxem1qbXF3MWZLZExTcUoyN01MdTdqTjh0cWgifQ==",
            )
            store1 = Store(
                id="01YCP46JKYM8FJCQ37NMBYHE5X",
                name="store1",
                created_at=datetime.fromisoformat("2022-07-25T21:15:37.524+00:00"),
                updated_at=datetime.fromisoformat("2022-07-25T21:15:37.524+00:00"),
                deleted_at=datetime.fromisoformat("2022-07-25T21:15:37.524+00:00"),
            )
            store2 = Store(
                id="01YCP46JKYM8FJCQ37NMBYHE6X",
                name="store2",
                created_at=datetime.fromisoformat("2022-07-25T21:15:37.524+00:00"),
                updated_at=datetime.fromisoformat("2022-07-25T21:15:37.524+00:00"),
                deleted_at=datetime.fromisoformat("2022-07-25T21:15:37.524+00:00"),
            )

            stores = [store1, store2]
            self.assertEqual(api_response.stores, stores)
            mock_request.assert_called_once_with(
                "GET",
                "http://api.fga.example/stores",
                headers=ANY,
                body=None,
                query_params=[
                    ("page_size", 1),
                    ("continuation_token", "continuation_token_example"),
                ],
                post_params=[],
                _preload_content=ANY,
                _request_timeout=None,
            )
            await api_client.close()

    @patch.object(rest.RESTClientObject, "request")
    async def test_list_stores_with_name(self, mock_request):
        """Test list_stores with name option"""
        continuation_token = uuid.uuid4().hex

        response_body = json.dumps(
            {
                "stores": [
                    {
                        "id": "01H0K5JSRNKM3P8T1SVZ9RGX90",
                        "name": "test-store",
                        "created_at": "2022-07-25T21:15:37.524Z",
                        "updated_at": "2022-07-25T21:15:37.524Z",
                        "deleted_at": "2022-07-25T21:15:37.524Z",
                    }
                ],
                "continuation_token": continuation_token,
            }
        )

        store = Store(
            id="01H0K5JSRNKM3P8T1SVZ9RGX90",
            name="test-store",
            created_at=datetime.fromisoformat("2022-07-25T21:15:37.524+00:00"),
            updated_at=datetime.fromisoformat("2022-07-25T21:15:37.524+00:00"),
            deleted_at=datetime.fromisoformat("2022-07-25T21:15:37.524+00:00"),
        )

        mock_request.return_value = mock_response(response_body, 200)
        configuration = self.configuration

        async with OpenFgaClient(configuration) as api_client:
            api_response = await api_client.list_stores(
                options={
                    "name": "test-store",
                    "page_size": 1,
                    "continuation_token": continuation_token,
                }
            )

            self.assertIsInstance(api_response, ListStoresResponse)
            self.assertEqual(api_response.continuation_token, continuation_token)
            self.assertEqual(len(api_response.stores), 1)
            self.assertEqual(api_response.stores[0], store)
            self.assertEqual(api_response.stores[0].name, "test-store")
            self.assertEqual(api_response.stores[0].id, "01H0K5JSRNKM3P8T1SVZ9RGX90")

            mock_request.assert_called_once_with(
                "GET",
                "http://api.fga.example/stores",
                headers=ANY,
                body=ANY,
                query_params=[
                    ("page_size", 1),
                    ("continuation_token", continuation_token),
                    ("name", "test-store"),
                ],
                post_params=ANY,
                _preload_content=ANY,
                _request_timeout=ANY,
            )

    @patch.object(rest.RESTClientObject, "request")
    async def test_create_store(self, mock_request):
        """Test case for create_store

        Create a store
        """
        response_body = """{
            "id": "01YCP46JKYM8FJCQ37NMBYHE5X",
            "name": "test_store",
            "created_at": "2022-07-25T17:41:26.607Z",
            "updated_at": "2022-07-25T17:41:26.607Z"}
            """
        mock_request.return_value = mock_response(response_body, 201)
        configuration = self.configuration
        async with OpenFgaClient(configuration) as api_client:
            api_response = await api_client.create_store(
                CreateStoreRequest(name="test-store"), options={}
            )
            self.assertIsInstance(api_response, CreateStoreResponse)
            self.assertEqual(api_response.id, "01YCP46JKYM8FJCQ37NMBYHE5X")
            mock_request.assert_called_once_with(
                "POST",
                "http://api.fga.example/stores",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={"name": "test-store"},
                _preload_content=ANY,
                _request_timeout=None,
            )
            await api_client.close()

    @patch.object(rest.RESTClientObject, "request")
    async def test_get_store(self, mock_request):
        """Test case for get_store

        Get all stores
        """
        response_body = """
{
    "id": "01YCP46JKYM8FJCQ37NMBYHE5X",
    "name": "store1",
    "created_at": "2022-07-25T21:15:37.524Z",
    "updated_at": "2022-07-25T21:15:37.524Z"
}
            """
        mock_request.return_value = mock_response(response_body, 200)
        configuration = self.configuration
        configuration.store_id = store_id
        async with OpenFgaClient(configuration) as api_client:
            api_response = await api_client.get_store(options={})
            self.assertIsInstance(api_response, GetStoreResponse)
            self.assertEqual(api_response.id, "01YCP46JKYM8FJCQ37NMBYHE5X")
            self.assertEqual(api_response.name, "store1")
            mock_request.assert_called_once_with(
                "GET",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X",
                headers=ANY,
                body=None,
                query_params=[],
                post_params=[],
                _preload_content=ANY,
                _request_timeout=None,
            )
            await api_client.close()

    @patch.object(rest.RESTClientObject, "request")
    async def test_delete_store(self, mock_request):
        """Test case for delete_store

        Get all stores
        """
        mock_request.return_value = mock_response("", 201)
        configuration = self.configuration
        configuration.store_id = store_id
        async with OpenFgaClient(configuration) as api_client:
            await api_client.delete_store(options={})
            mock_request.assert_called_once_with(
                "DELETE",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X",
                headers=ANY,
                body=None,
                query_params=[],
                post_params=[],
                _preload_content=ANY,
                _request_timeout=None,
            )
            await api_client.close()

    @patch.object(rest.RESTClientObject, "request")
    async def test_read_authorization_models(self, mock_request):
        """Test case for read_authorization_models

        Return all authorization models configured for the store
        """
        response_body = """
{
  "authorization_models": [{
    "id": "01G5JAVJ41T49E9TT3SKVS7X1J",
    "schema_version":"1.1",
    "type_definitions": [
      {
        "type": "document",
        "relations": {
          "reader": {
            "union": {
              "child": [
                {
                  "this": {}
                },
                {
                  "computedUserset": {
                    "object": "",
                    "relation": "writer"
                  }
                }
              ]
            }
          },
          "writer": {
            "this": {}
          }
        }
      }
    ]
  }],
  "continuation_token": "eyJwayI6IkxBVEVTVF9OU0NPTkZJR19hdXRoMHN0b3JlIiwic2siOiIxem1qbXF3MWZLZExTcUoyN01MdTdqTjh0cWgifQ=="
}
        """
        mock_request.return_value = mock_response(response_body, 200)
        configuration = self.configuration
        configuration.store_id = store_id
        # Enter a context with an instance of the API client
        async with OpenFgaClient(configuration) as api_client:
            # Return a particular version of an authorization model
            api_response = await api_client.read_authorization_models(options={})
            self.assertIsInstance(api_response, ReadAuthorizationModelsResponse)
            type_definitions = [
                TypeDefinition(
                    type="document",
                    relations=dict(
                        reader=Userset(
                            union=Usersets(
                                child=[
                                    Userset(this=dict()),
                                    Userset(
                                        computed_userset=ObjectRelation(
                                            object="",
                                            relation="writer",
                                        )
                                    ),
                                ],
                            ),
                        ),
                        writer=Userset(
                            this=dict(),
                        ),
                    ),
                )
            ]
            authorization_model = AuthorizationModel(
                id="01G5JAVJ41T49E9TT3SKVS7X1J",
                schema_version="1.1",
                type_definitions=type_definitions,
            )
            self.assertEqual(api_response.authorization_models, [authorization_model])
            self.assertEqual(
                api_response.continuation_token,
                "eyJwayI6IkxBVEVTVF9OU0NPTkZJR19hdXRoMHN0b3JlIiwic2siOiIxem1qbXF3MWZLZExTcUoyN01MdTdqTjh0cWgifQ==",
            )
            mock_request.assert_called_once_with(
                "GET",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/authorization-models",
                headers=ANY,
                body=None,
                query_params=[],
                post_params=[],
                _preload_content=ANY,
                _request_timeout=None,
            )

    @patch.object(rest.RESTClientObject, "request")
    async def test_write_authorization_model(self, mock_request):
        """Test case for write_authorization_model

        Create a new authorization model
        """
        response_body = '{"authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J"}'
        mock_request.return_value = mock_response(response_body, 201)
        configuration = self.configuration
        configuration.store_id = store_id
        async with OpenFgaClient(configuration) as api_client:
            # example passing only required values which don't have defaults set
            body = WriteAuthorizationModelRequest(
                schema_version="1.1",
                type_definitions=[
                    TypeDefinition(
                        type="document",
                        relations=dict(
                            writer=Userset(
                                this=dict(),
                            ),
                            reader=Userset(
                                union=Usersets(
                                    child=[
                                        Userset(this=dict()),
                                        Userset(
                                            computed_userset=ObjectRelation(
                                                object="",
                                                relation="writer",
                                            )
                                        ),
                                    ],
                                ),
                            ),
                        ),
                    ),
                ],
            )
            # Create a new authorization model
            api_response = await api_client.write_authorization_model(body, options={})
            self.assertIsInstance(api_response, WriteAuthorizationModelResponse)
            expected_response = WriteAuthorizationModelResponse(
                authorization_model_id="01G5JAVJ41T49E9TT3SKVS7X1J"
            )
            self.assertEqual(api_response, expected_response)
            mock_request.assert_called_once_with(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/authorization-models",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "schema_version": "1.1",
                    "type_definitions": [
                        {
                            "type": "document",
                            "relations": {
                                "writer": {"this": {}},
                                "reader": {
                                    "union": {
                                        "child": [
                                            {"this": {}},
                                            {
                                                "computedUserset": {
                                                    "object": "",
                                                    "relation": "writer",
                                                }
                                            },
                                        ]
                                    }
                                },
                            },
                        }
                    ],
                },
                _preload_content=ANY,
                _request_timeout=None,
            )

    @patch.object(rest.RESTClientObject, "request")
    async def test_read_authorization_model(self, mock_request):
        """Test case for read_authorization_model

        Return a particular version of an authorization model
        """
        response_body = """
{
  "authorization_model": {
    "id": "01G5JAVJ41T49E9TT3SKVS7X1J",
    "schema_version":"1.1",
    "type_definitions": [
      {
        "type": "document",
        "relations": {
          "reader": {
            "union": {
              "child": [
                {
                  "this": {}
                },
                {
                  "computedUserset": {
                    "object": "",
                    "relation": "writer"
                  }
                }
              ]
            }
          },
          "writer": {
            "this": {}
          }
        }
      }
    ]
  }
}
        """
        mock_request.return_value = mock_response(response_body, 200)
        configuration = self.configuration
        configuration.store_id = store_id
        # Enter a context with an instance of the API client
        async with OpenFgaClient(configuration) as api_client:
            # Return a particular version of an authorization model
            api_response = await api_client.read_authorization_model(
                options={"authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J"}
            )
            self.assertIsInstance(api_response, ReadAuthorizationModelResponse)
            type_definitions = [
                TypeDefinition(
                    type="document",
                    relations=dict(
                        reader=Userset(
                            union=Usersets(
                                child=[
                                    Userset(this=dict()),
                                    Userset(
                                        computed_userset=ObjectRelation(
                                            object="",
                                            relation="writer",
                                        )
                                    ),
                                ],
                            ),
                        ),
                        writer=Userset(
                            this=dict(),
                        ),
                    ),
                )
            ]
            authorization_model = AuthorizationModel(
                id="01G5JAVJ41T49E9TT3SKVS7X1J",
                schema_version="1.1",
                type_definitions=type_definitions,
            )
            self.assertEqual(api_response.authorization_model, authorization_model)
            mock_request.assert_called_once_with(
                "GET",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/authorization-models/01G5JAVJ41T49E9TT3SKVS7X1J",
                headers=ANY,
                body=None,
                query_params=[],
                post_params=[],
                _preload_content=ANY,
                _request_timeout=None,
            )

    @patch.object(rest.RESTClientObject, "request")
    async def test_read_latest_authorization_model(self, mock_request):
        """Test case for read_latest_authorization_model

        Return the latest authorization models configured for the store
        """
        response_body = """
{
  "authorization_models": [{
    "id": "01G5JAVJ41T49E9TT3SKVS7X1J",
    "schema_version":"1.1",
    "type_definitions": [
      {
        "type": "document",
        "relations": {
          "reader": {
            "union": {
              "child": [
                {
                  "this": {}
                },
                {
                  "computedUserset": {
                    "object": "",
                    "relation": "writer"
                  }
                }
              ]
            }
          },
          "writer": {
            "this": {}
          }
        }
      }
    ]
  }],
  "continuation_token": "eyJwayI6IkxBVEVTVF9OU0NPTkZJR19hdXRoMHN0b3JlIiwic2siOiIxem1qbXF3MWZLZExTcUoyN01MdTdqTjh0cWgifQ=="
}
        """
        mock_request.return_value = mock_response(response_body, 200)
        configuration = self.configuration
        configuration.store_id = store_id
        # Enter a context with an instance of the API client
        async with OpenFgaClient(configuration) as api_client:
            # Return a particular version of an authorization model
            api_response = await api_client.read_latest_authorization_model(options={})
            self.assertIsInstance(api_response, ReadAuthorizationModelResponse)
            type_definitions = [
                TypeDefinition(
                    type="document",
                    relations=dict(
                        reader=Userset(
                            union=Usersets(
                                child=[
                                    Userset(this=dict()),
                                    Userset(
                                        computed_userset=ObjectRelation(
                                            object="",
                                            relation="writer",
                                        )
                                    ),
                                ],
                            ),
                        ),
                        writer=Userset(
                            this=dict(),
                        ),
                    ),
                )
            ]
            authorization_model = AuthorizationModel(
                id="01G5JAVJ41T49E9TT3SKVS7X1J",
                schema_version="1.1",
                type_definitions=type_definitions,
            )
            self.assertEqual(api_response.authorization_model, authorization_model)
            mock_request.assert_called_once_with(
                "GET",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/authorization-models",
                headers=ANY,
                body=None,
                query_params=[("page_size", 1)],
                post_params=[],
                _preload_content=ANY,
                _request_timeout=None,
            )

    @patch.object(rest.RESTClientObject, "request")
    async def test_read_latest_authorization_model_with_no_models(self, mock_request):
        """Test case for read_latest_authorization_model when no models are in the store

        Return the latest authorization models configured for the store
        """
        response_body = """
{
  "authorization_models": []
}
        """
        mock_request.return_value = mock_response(response_body, 200)
        configuration = self.configuration
        configuration.store_id = store_id
        # Enter a context with an instance of the API client
        async with OpenFgaClient(configuration) as api_client:
            # Return a particular version of an authorization model
            api_response = await api_client.read_latest_authorization_model(options={})
            self.assertIsInstance(api_response, ReadAuthorizationModelResponse)
            self.assertIsNone(api_response.authorization_model)
            mock_request.assert_called_once_with(
                "GET",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/authorization-models",
                headers=ANY,
                body=None,
                query_params=[("page_size", 1)],
                post_params=[],
                _preload_content=ANY,
                _request_timeout=None,
            )

    @patch.object(rest.RESTClientObject, "request")
    async def test_read_changes(self, mock_request):
        """Test case for read_changes

        Return a list of all the tuple changes
        """
        response_body = """
{
  "changes": [
    {
      "tuple_key": {
        "object": "document:2021-budget",
        "relation": "reader",
        "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b"
      },
      "operation": "TUPLE_OPERATION_WRITE",
      "timestamp": "2022-07-26T15:55:55.809Z"
    }
  ],
  "continuation_token": "eyJwayI6IkxBVEVTVF9OU0NPTkZJR19hdXRoMHN0b3JlIiwic2siOiIxem1qbXF3MWZLZExTcUoyN01MdTdqTjh0cWgifQ=="
}
        """
        mock_request.return_value = mock_response(response_body, 200)
        configuration = self.configuration
        configuration.store_id = store_id
        # Enter a context with an instance of the API client
        async with OpenFgaClient(configuration) as api_client:
            # Return a particular version of an authorization model
            api_response = await api_client.read_changes(
                ClientReadChangesRequest("document", "2022-01-01T00:00:00+00:00"),
                options={"page_size": 1, "continuation_token": "abcdefg"},
            )

            self.assertIsInstance(api_response, ReadChangesResponse)
            changes = TupleChange(
                tuple_key=TupleKey(
                    object="document:2021-budget",
                    relation="reader",
                    user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                ),
                operation=TupleOperation.WRITE,
                timestamp=datetime.fromisoformat("2022-07-26T15:55:55.809+00:00"),
            )
            read_changes = ReadChangesResponse(
                continuation_token="eyJwayI6IkxBVEVTVF9OU0NPTkZJR19hdXRoMHN0b3JlIiwic2siOiIxem1qbXF3MWZLZExTcUoyN01MdTdqTjh0cWgifQ==",
                changes=[changes],
            )
            self.assertEqual(api_response, read_changes)
            mock_request.assert_called_once_with(
                "GET",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/changes",
                headers=ANY,
                body=None,
                query_params=[
                    ("type", "document"),
                    ("page_size", 1),
                    ("continuation_token", "abcdefg"),
                    ("start_time", "2022-01-01T00:00:00+00:00"),
                ],
                post_params=[],
                _preload_content=ANY,
                _request_timeout=None,
            )

    @patch.object(rest.RESTClientObject, "request")
    async def test_read(self, mock_request):
        """Test case for read

        Get tuples from the store that matches a query, without following userset rewrite rules
        """
        response_body = """
            {
  "tuples": [
    {
      "key": {
        "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b",
        "relation": "reader",
        "object": "document:2021-budget"
      },
      "timestamp": "2021-10-06T15:32:11.128Z"
    }
  ],
  "continuation_token": ""
}
        """
        mock_request.return_value = mock_response(response_body, 200)
        configuration = self.configuration
        configuration.store_id = store_id
        # Enter a context with an instance of the API client
        async with OpenFgaClient(configuration) as api_client:
            body = ReadRequestTupleKey(
                object="document:2021-budget",
                relation="reader",
                user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
            )
            api_response = await api_client.read(
                body=body,
                options={
                    "page_size": 50,
                    "continuation_token": "eyJwayI6IkxBVEVTVF9OU0NPTkZJR19hdXRoMHN0b3JlIiwic2siOiIxem1qbXF3MWZLZExTcUoyN01MdTdqTjh0cWgifQ==",
                    "consistency": ConsistencyPreference.MINIMIZE_LATENCY,
                    "retry_params": RetryParams(max_retry=3, min_wait_in_ms=1000),
                },
            )
            self.assertIsInstance(api_response, ReadResponse)
            key = TupleKey(
                user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                relation="reader",
                object="document:2021-budget",
            )
            timestamp = datetime.fromisoformat("2021-10-06T15:32:11.128+00:00")
            expected_data = ReadResponse(
                tuples=[Tuple(key=key, timestamp=timestamp)], continuation_token=""
            )
            self.assertEqual(api_response, expected_data)
            mock_request.assert_called_once_with(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/read",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "tuple_key": {
                        "object": "document:2021-budget",
                        "relation": "reader",
                        "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                    },
                    "page_size": 50,
                    "continuation_token": "eyJwayI6IkxBVEVTVF9OU0NPTkZJR19hdXRoMHN0b3JlIiwic2siOiIxem1qbXF3MWZLZExTcUoyN01MdTdqTjh0cWgifQ==",
                    "consistency": "MINIMIZE_LATENCY",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )

    @patch.object(rest.RESTClientObject, "request")
    async def test_read_empty_options(self, mock_request):
        """Test case for read with empty options

        Get tuples from the store that matches a query, without following userset rewrite rules
        """
        response_body = """
            {
  "tuples": [
    {
      "key": {
        "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b",
        "relation": "reader",
        "object": "document:2021-budget"
      },
      "timestamp": "2021-10-06T15:32:11.128Z"
    }
  ],
  "continuation_token": ""
}
        """
        mock_request.return_value = mock_response(response_body, 200)
        configuration = self.configuration
        configuration.store_id = store_id
        # Enter a context with an instance of the API client
        async with OpenFgaClient(configuration) as api_client:
            body = ReadRequestTupleKey(
                object="document:2021-budget",
                relation="reader",
                user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
            )
            api_response = await api_client.read(body=body, options={})
            self.assertIsInstance(api_response, ReadResponse)
            key = TupleKey(
                user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                relation="reader",
                object="document:2021-budget",
            )
            timestamp = datetime.fromisoformat("2021-10-06T15:32:11.128+00:00")
            expected_data = ReadResponse(
                tuples=[Tuple(key=key, timestamp=timestamp)], continuation_token=""
            )
            self.assertEqual(api_response, expected_data)
            mock_request.assert_called_once_with(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/read",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "tuple_key": {
                        "object": "document:2021-budget",
                        "relation": "reader",
                        "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                    }
                },
                _preload_content=ANY,
                _request_timeout=None,
            )

    @patch.object(rest.RESTClientObject, "request")
    async def test_read_empty_body(self, mock_request):
        """Test case for read with empty body

        Get tuples from the store that matches a query, without following userset rewrite rules
        """
        response_body = """
            {
  "tuples": [
    {
      "key": {
        "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b",
        "relation": "reader",
        "object": "document:2021-budget"
      },
      "timestamp": "2021-10-06T15:32:11.128Z"
    }
  ],
  "continuation_token": ""
}
        """
        mock_request.return_value = mock_response(response_body, 200)
        configuration = self.configuration
        configuration.store_id = store_id
        # Enter a context with an instance of the API client
        async with OpenFgaClient(configuration) as api_client:
            body = ReadRequestTupleKey()
            api_response = await api_client.read(body=body, options={})
            self.assertIsInstance(api_response, ReadResponse)
            key = TupleKey(
                user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                relation="reader",
                object="document:2021-budget",
            )
            timestamp = datetime.fromisoformat("2021-10-06T15:32:11.128+00:00")
            expected_data = ReadResponse(
                tuples=[Tuple(key=key, timestamp=timestamp)], continuation_token=""
            )
            self.assertEqual(api_response, expected_data)
            mock_request.assert_called_once_with(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/read",
                headers=ANY,
                body={},
                query_params=[],
                post_params=[],
                _preload_content=ANY,
                _request_timeout=None,
            )

    @patch.object(rest.RESTClientObject, "request")
    async def test_write(self, mock_request):
        """Test case for write

        Add tuples from the store with transaction enabled
        """
        response_body = "{}"
        mock_request.return_value = mock_response(response_body, 200)
        configuration = self.configuration
        configuration.store_id = store_id
        async with OpenFgaClient(configuration) as api_client:
            body = ClientWriteRequest(
                writes=[
                    ClientTuple(
                        object="document:2021-budget",
                        relation="reader",
                        user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                    ),
                    ClientTuple(
                        object="document:2021-budget",
                        relation="reader",
                        user="user:81684243-9356-4421-8fbf-a4f8d36aa31c",
                    ),
                    ClientTuple(
                        object="document:2021-budget",
                        relation="reader",
                        user="user:81684243-9356-4421-8fbf-a4f8d36aa31d",
                    ),
                ],
            )
            await api_client.write(
                body, options={"authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J"}
            )
            mock_request.assert_called_once_with(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/write",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "writes": {
                        "tuple_keys": [
                            {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                            },
                            {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31c",
                            },
                            {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31d",
                            },
                        ],
                        "on_duplicate": "error",
                    },
                    "authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )

    @patch.object(rest.RESTClientObject, "request")
    async def test_delete(self, mock_request):
        """Test case for delete

        Delete tuples from the store with transaction enabled
        """
        response_body = "{}"
        mock_request.return_value = mock_response(response_body, 200)
        configuration = self.configuration
        configuration.store_id = store_id
        async with OpenFgaClient(configuration) as api_client:
            body = ClientWriteRequest(
                deletes=[
                    ClientTuple(
                        object="document:2021-budget",
                        relation="reader",
                        user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                    )
                ],
            )
            await api_client.write(
                body, options={"authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J"}
            )
            mock_request.assert_called_once_with(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/write",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "deletes": {
                        "tuple_keys": [
                            {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                            }
                        ],
                        "on_missing": "error",
                    },
                    "authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )

    @patch.object(rest.RESTClientObject, "request")
    async def test_write_batch(self, mock_request):
        """Test case for write

        Add tuples from the store with transaction disabled
        """
        mock_request.side_effect = [
            mock_response("{}", 200),
            mock_response("{}", 200),
            mock_response("{}", 200),
        ]
        configuration = self.configuration
        configuration.store_id = store_id
        async with OpenFgaClient(configuration) as api_client:
            body = ClientWriteRequest(
                writes=[
                    ClientTuple(
                        object="document:2021-budget",
                        relation="reader",
                        user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                    ),
                    ClientTuple(
                        object="document:2021-budget",
                        relation="reader",
                        user="user:81684243-9356-4421-8fbf-a4f8d36aa31c",
                    ),
                    ClientTuple(
                        object="document:2021-budget",
                        relation="reader",
                        user="user:81684243-9356-4421-8fbf-a4f8d36aa31d",
                    ),
                ],
            )
            transaction = WriteTransactionOpts(
                disabled=True, max_per_chunk=1, max_parallel_requests=10
            )
            response = await api_client.write(
                body,
                options={
                    "authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J",
                    "transaction": transaction,
                },
            )

            self.assertEqual(response.deletes, None)
            self.assertEqual(
                response.writes,
                [
                    ClientWriteSingleResponse(
                        tuple_key=ClientTuple(
                            object="document:2021-budget",
                            relation="reader",
                            user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                        ),
                        success=True,
                        error=None,
                    ),
                    ClientWriteSingleResponse(
                        tuple_key=ClientTuple(
                            object="document:2021-budget",
                            relation="reader",
                            user="user:81684243-9356-4421-8fbf-a4f8d36aa31c",
                        ),
                        success=True,
                        error=None,
                    ),
                    ClientWriteSingleResponse(
                        tuple_key=ClientTuple(
                            object="document:2021-budget",
                            relation="reader",
                            user="user:81684243-9356-4421-8fbf-a4f8d36aa31d",
                        ),
                        success=True,
                        error=None,
                    ),
                ],
            )
            self.assertEqual(mock_request.call_count, 3)
            mock_request.assert_any_call(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/write",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "writes": {
                        "tuple_keys": [
                            {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                            }
                        ],
                        "on_duplicate": "error",
                    },
                    "authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )
            mock_request.assert_any_call(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/write",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "writes": {
                        "tuple_keys": [
                            {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31c",
                            }
                        ],
                        "on_duplicate": "error",
                    },
                    "authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )
            mock_request.assert_any_call(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/write",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "writes": {
                        "tuple_keys": [
                            {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31d",
                            }
                        ],
                        "on_duplicate": "error",
                    },
                    "authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )

    @patch.object(rest.RESTClientObject, "request")
    async def test_write_batch_min_parallel(self, mock_request):
        """Test case for write

        Add tuples from the store with transaction disabled and minimum parallel request
        """
        mock_request.side_effect = [
            mock_response("{}", 200),
            mock_response("{}", 200),
            mock_response("{}", 200),
        ]
        configuration = self.configuration
        configuration.store_id = store_id
        async with OpenFgaClient(configuration) as api_client:
            body = ClientWriteRequest(
                writes=[
                    ClientTuple(
                        object="document:2021-budget",
                        relation="reader",
                        user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                    ),
                    ClientTuple(
                        object="document:2021-budget",
                        relation="reader",
                        user="user:81684243-9356-4421-8fbf-a4f8d36aa31c",
                    ),
                    ClientTuple(
                        object="document:2021-budget",
                        relation="reader",
                        user="user:81684243-9356-4421-8fbf-a4f8d36aa31d",
                    ),
                ],
            )
            transaction = WriteTransactionOpts(
                disabled=True, max_per_chunk=1, max_parallel_requests=1
            )
            response = await api_client.write(
                body,
                options={
                    "authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J",
                    "transaction": transaction,
                },
            )

            self.assertEqual(response.deletes, None)
            self.assertEqual(
                response.writes,
                [
                    ClientWriteSingleResponse(
                        tuple_key=ClientTuple(
                            object="document:2021-budget",
                            relation="reader",
                            user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                        ),
                        success=True,
                        error=None,
                    ),
                    ClientWriteSingleResponse(
                        tuple_key=ClientTuple(
                            object="document:2021-budget",
                            relation="reader",
                            user="user:81684243-9356-4421-8fbf-a4f8d36aa31c",
                        ),
                        success=True,
                        error=None,
                    ),
                    ClientWriteSingleResponse(
                        tuple_key=ClientTuple(
                            object="document:2021-budget",
                            relation="reader",
                            user="user:81684243-9356-4421-8fbf-a4f8d36aa31d",
                        ),
                        success=True,
                        error=None,
                    ),
                ],
            )
            self.assertEqual(mock_request.call_count, 3)
            mock_request.assert_any_call(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/write",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "writes": {
                        "tuple_keys": [
                            {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                            }
                        ],
                        "on_duplicate": "error",
                    },
                    "authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )
            mock_request.assert_any_call(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/write",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "writes": {
                        "tuple_keys": [
                            {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31c",
                            }
                        ],
                        "on_duplicate": "error",
                    },
                    "authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )
            mock_request.assert_any_call(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/write",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "writes": {
                        "tuple_keys": [
                            {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31d",
                            }
                        ],
                        "on_duplicate": "error",
                    },
                    "authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )

    @patch.object(rest.RESTClientObject, "request")
    async def test_write_batch_larger_chunk(self, mock_request):
        """Test case for write

        Add tuples from the store with transaction disabled and minimum parallel request
        """
        mock_request.side_effect = [
            mock_response("{}", 200),
            mock_response("{}", 200),
        ]
        configuration = self.configuration
        configuration.store_id = store_id
        async with OpenFgaClient(configuration) as api_client:
            body = ClientWriteRequest(
                writes=[
                    ClientTuple(
                        object="document:2021-budget",
                        relation="reader",
                        user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                    ),
                    ClientTuple(
                        object="document:2021-budget",
                        relation="reader",
                        user="user:81684243-9356-4421-8fbf-a4f8d36aa31c",
                    ),
                    ClientTuple(
                        object="document:2021-budget",
                        relation="reader",
                        user="user:81684243-9356-4421-8fbf-a4f8d36aa31d",
                    ),
                ],
            )
            transaction = WriteTransactionOpts(
                disabled=True, max_per_chunk=2, max_parallel_requests=2
            )
            response = await api_client.write(
                body,
                options={
                    "authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J",
                    "transaction": transaction,
                },
            )

            self.assertEqual(response.deletes, None)
            self.assertEqual(
                response.writes,
                [
                    ClientWriteSingleResponse(
                        tuple_key=ClientTuple(
                            object="document:2021-budget",
                            relation="reader",
                            user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                        ),
                        success=True,
                        error=None,
                    ),
                    ClientWriteSingleResponse(
                        tuple_key=ClientTuple(
                            object="document:2021-budget",
                            relation="reader",
                            user="user:81684243-9356-4421-8fbf-a4f8d36aa31c",
                        ),
                        success=True,
                        error=None,
                    ),
                    ClientWriteSingleResponse(
                        tuple_key=ClientTuple(
                            object="document:2021-budget",
                            relation="reader",
                            user="user:81684243-9356-4421-8fbf-a4f8d36aa31d",
                        ),
                        success=True,
                        error=None,
                    ),
                ],
            )
            self.assertEqual(mock_request.call_count, 2)
            mock_request.assert_any_call(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/write",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "writes": {
                        "tuple_keys": [
                            {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                            },
                            {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31c",
                            },
                        ],
                        "on_duplicate": "error",
                    },
                    "authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )
            mock_request.assert_any_call(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/write",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "writes": {
                        "tuple_keys": [
                            {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31d",
                            }
                        ],
                        "on_duplicate": "error",
                    },
                    "authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )

    @patch.object(rest.RESTClientObject, "request")
    async def test_write_batch_failed(self, mock_request):
        """Test case for write

        Add tuples from the store with transaction disabled where one of the request failed
        """
        response_body = """
{
  "code": "validation_error",
  "message": "Generic validation error"
}
        """

        mock_request.side_effect = [
            mock_response("{}", 200),
            ValidationException(http_resp=http_mock_response(response_body, 400)),
            mock_response("{}", 200),
        ]
        configuration = self.configuration
        configuration.store_id = store_id
        async with OpenFgaClient(configuration) as api_client:
            body = ClientWriteRequest(
                writes=[
                    ClientTuple(
                        object="document:2021-budget",
                        relation="reader",
                        user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                    ),
                    ClientTuple(
                        object="document:2021-budget",
                        relation="reader",
                        user="user:81684243-9356-4421-8fbf-a4f8d36aa31c",
                    ),
                    ClientTuple(
                        object="document:2021-budget",
                        relation="reader",
                        user="user:81684243-9356-4421-8fbf-a4f8d36aa31d",
                    ),
                ],
            )
            transaction = WriteTransactionOpts(
                disabled=True, max_per_chunk=1, max_parallel_requests=10
            )
            response = await api_client.write(
                body,
                options={
                    "authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J",
                    "transaction": transaction,
                },
            )

            self.assertEqual(response.deletes, None)
            self.assertEqual(len(response.writes), 3)
            self.assertEqual(
                response.writes[0],
                ClientWriteSingleResponse(
                    tuple_key=ClientTuple(
                        object="document:2021-budget",
                        relation="reader",
                        user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                    ),
                    success=True,
                    error=None,
                ),
            )
            self.assertEqual(
                response.writes[1].tuple_key,
                ClientTuple(
                    object="document:2021-budget",
                    relation="reader",
                    user="user:81684243-9356-4421-8fbf-a4f8d36aa31c",
                ),
            )
            self.assertFalse(response.writes[1].success)
            self.assertIsInstance(response.writes[1].error, ValidationException)
            self.assertIsInstance(
                response.writes[1].error.parsed_exception,
                ValidationErrorMessageResponse,
            )
            self.assertEqual(
                response.writes[2],
                ClientWriteSingleResponse(
                    tuple_key=ClientTuple(
                        object="document:2021-budget",
                        relation="reader",
                        user="user:81684243-9356-4421-8fbf-a4f8d36aa31d",
                    ),
                    success=True,
                    error=None,
                ),
            )
            self.assertEqual(mock_request.call_count, 3)
            mock_request.assert_any_call(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/write",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "writes": {
                        "tuple_keys": [
                            {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                            }
                        ],
                        "on_duplicate": "error",
                    },
                    "authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )
            mock_request.assert_any_call(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/write",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "writes": {
                        "tuple_keys": [
                            {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31c",
                            }
                        ],
                        "on_duplicate": "error",
                    },
                    "authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )
            mock_request.assert_any_call(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/write",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "writes": {
                        "tuple_keys": [
                            {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31d",
                            }
                        ],
                        "on_duplicate": "error",
                    },
                    "authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )

    @patch.object(rest.RESTClientObject, "request")
    async def test_delete_batch(self, mock_request):
        """Test case for delete

        Delete tuples from the store with transaction disabled but there is only 1 relationship tuple
        """
        mock_request.side_effect = [
            mock_response("{}", 200),
        ]
        configuration = self.configuration
        configuration.store_id = store_id
        async with OpenFgaClient(configuration) as api_client:
            body = ClientWriteRequest(
                deletes=[
                    ClientTuple(
                        object="document:2021-budget",
                        relation="reader",
                        user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                    )
                ],
                writes=[],
            )
            transaction = WriteTransactionOpts(
                disabled=True, max_per_chunk=1, max_parallel_requests=10
            )
            await api_client.write(
                body,
                options={
                    "authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J",
                    "transaction": transaction,
                },
            )
            mock_request.assert_any_call(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/write",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "deletes": {
                        "tuple_keys": [
                            {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                            }
                        ],
                        "on_missing": "error",
                    },
                    "authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )

    @patch.object(rest.RESTClientObject, "request")
    async def test_write_tuples(self, mock_request):
        """Test case for write tuples

        Add tuples from the store with transaction enabled
        """
        response_body = "{}"
        mock_request.return_value = mock_response(response_body, 200)
        configuration = self.configuration
        configuration.store_id = store_id
        async with OpenFgaClient(configuration) as api_client:
            await api_client.write_tuples(
                [
                    ClientTuple(
                        object="document:2021-budget",
                        relation="reader",
                        user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                    ),
                    ClientTuple(
                        object="document:2021-budget",
                        relation="reader",
                        user="user:81684243-9356-4421-8fbf-a4f8d36aa31c",
                    ),
                    ClientTuple(
                        object="document:2021-budget",
                        relation="reader",
                        user="user:81684243-9356-4421-8fbf-a4f8d36aa31d",
                    ),
                ],
                options={"authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J"},
            )
            mock_request.assert_called_once_with(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/write",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "writes": {
                        "tuple_keys": [
                            {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                            },
                            {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31c",
                            },
                            {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31d",
                            },
                        ],
                        "on_duplicate": "error",
                    },
                    "authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )

    @patch.object(rest.RESTClientObject, "request")
    async def test_delete_tuples(self, mock_request):
        """Test case for delete tuples

        Add tuples from the store with transaction enabled
        """
        response_body = "{}"
        mock_request.return_value = mock_response(response_body, 200)
        configuration = self.configuration
        configuration.store_id = store_id
        async with OpenFgaClient(configuration) as api_client:
            await api_client.delete_tuples(
                [
                    ClientTuple(
                        object="document:2021-budget",
                        relation="reader",
                        user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                    ),
                    ClientTuple(
                        object="document:2021-budget",
                        relation="reader",
                        user="user:81684243-9356-4421-8fbf-a4f8d36aa31c",
                    ),
                    ClientTuple(
                        object="document:2021-budget",
                        relation="reader",
                        user="user:81684243-9356-4421-8fbf-a4f8d36aa31d",
                    ),
                ],
                options={"authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J"},
            )
            mock_request.assert_called_once_with(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/write",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "deletes": {
                        "tuple_keys": [
                            {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                            },
                            {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31c",
                            },
                            {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31d",
                            },
                        ],
                        "on_missing": "error",
                    },
                    "authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )

    @patch.object(rest.RESTClientObject, "request")
    async def test_write_batch_unauthorized(self, mock_request):
        """Test case for write with 401 response"""

        mock_request.side_effect = UnauthorizedException(
            http_resp=http_mock_response("{}", 401)
        )
        configuration = self.configuration
        configuration.store_id = store_id
        async with OpenFgaClient(configuration) as api_client:
            with self.assertRaises(UnauthorizedException):
                body = ClientWriteRequest(
                    writes=[
                        ClientTuple(
                            object="document:2021-budget",
                            relation="reader",
                            user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                        )
                    ],
                )
                transaction = WriteTransactionOpts(
                    disabled=True, max_per_chunk=1, max_parallel_requests=10
                )
                await api_client.write(
                    body,
                    options={
                        "authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J",
                        "transaction": transaction,
                    },
                )

            mock_request.assert_called()
            self.assertEqual(mock_request.call_count, 1)

            mock_request.assert_called_once_with(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/write",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "writes": {
                        "tuple_keys": [
                            {
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                                "relation": "reader",
                                "object": "document:2021-budget",
                            }
                        ],
                        "on_duplicate": "error",
                    },
                    "authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J",
                },
                _preload_content=ANY,
                _request_timeout=ANY,
            )
            await api_client.close()

    @patch.object(rest.RESTClientObject, "request")
    async def test_check(self, mock_request):
        """Test case for check

        Check whether a user is authorized to access an object
        """

        # First, mock the response
        response_body = '{"allowed": true, "resolution": "1234"}'
        mock_request.return_value = mock_response(response_body, 200)
        body = ClientCheckRequest(
            user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
            relation="reader",
            object="document:budget",
            contextual_tuples=[
                ClientTuple(
                    user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                    relation="writer",
                    object="document:budget",
                ),
            ],
        )
        configuration = self.configuration
        configuration.store_id = store_id
        async with OpenFgaClient(configuration) as api_client:
            api_response = await api_client.check(
                body=body,
                options={
                    "authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1",
                    "consistency": ConsistencyPreference.MINIMIZE_LATENCY,
                },
            )
            self.assertIsInstance(api_response, CheckResponse)
            self.assertTrue(api_response.allowed)
            # Make sure the API was called with the right data
            mock_request.assert_called_once_with(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/check",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "tuple_key": {
                        "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                        "relation": "reader",
                        "object": "document:budget",
                    },
                    "contextual_tuples": {
                        "tuple_keys": [
                            {
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                                "relation": "writer",
                                "object": "document:budget",
                            }
                        ]
                    },
                    "authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1",
                    "consistency": "MINIMIZE_LATENCY",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )
            await api_client.close()

    @patch.object(rest.RESTClientObject, "request")
    async def test_check_config_auth_model(self, mock_request):
        """Test case for check

        Check whether a user is authorized to access an object and the auth model is already encoded in store
        """

        # First, mock the response
        response_body = '{"allowed": true, "resolution": "1234"}'
        mock_request.return_value = mock_response(response_body, 200)
        body = ClientCheckRequest(
            object="document:2021-budget",
            relation="reader",
            user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
        )
        configuration = self.configuration
        configuration.store_id = store_id
        configuration.authorization_model_id = "01GXSA8YR785C4FYS3C0RTG7B1"
        async with OpenFgaClient(configuration) as api_client:
            api_response = await api_client.check(body=body, options={})
            self.assertIsInstance(api_response, CheckResponse)
            self.assertTrue(api_response.allowed)
            # Make sure the API was called with the right data
            mock_request.assert_called_once_with(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/check",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "tuple_key": {
                        "object": "document:2021-budget",
                        "relation": "reader",
                        "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                    },
                    "authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )
            await api_client.close()

    @patch.object(rest.RESTClientObject, "request")
    async def test_client_batch_check_single_request(self, mock_request):
        """Test case for check with single request

        Check whether a user is authorized to access an object
        """

        # First, mock the response
        response_body = '{"allowed": true, "resolution": "1234"}'
        mock_request.side_effect = [
            mock_response(response_body, 200),
        ]
        body = ClientCheckRequest(
            object="document:2021-budget",
            relation="reader",
            user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
        )
        configuration = self.configuration
        configuration.store_id = store_id
        async with OpenFgaClient(configuration) as api_client:
            api_response = await api_client.client_batch_check(
                body=[body],
                options={"authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1"},
            )
            self.assertIsInstance(api_response, list)
            self.assertEqual(len(api_response), 1)
            self.assertEqual(api_response[0].error, None)
            self.assertTrue(api_response[0].allowed)
            self.assertEqual(api_response[0].request, body)
            # Make sure the API was called with the right data
            mock_request.assert_any_call(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/check",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "tuple_key": {
                        "object": "document:2021-budget",
                        "relation": "reader",
                        "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                    },
                    "authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )
            await api_client.close()

    @patch.object(rest.RESTClientObject, "request")
    async def test_client_batch_check_multiple_request(self, mock_request):
        """Test case for check with multiple request

        Check whether a user is authorized to access an object
        """

        body1 = ClientCheckRequest(
            object="document:2021-budget",
            relation="reader",
            user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
        )
        body2 = ClientCheckRequest(
            object="document:2021-budget",
            relation="reader",
            user="user:81684243-9356-4421-8fbf-a4f8d36aa31c",
        )
        body3 = ClientCheckRequest(
            object="document:2021-budget",
            relation="reader",
            user="user:81684243-9356-4421-8fbf-a4f8d36aa31d",
        )

        # Mock the response based on request body to avoid race conditions
        def mock_side_effect(*args, **kwargs):
            body = kwargs.get("body", {})
            user = body.get("tuple_key", {}).get("user", "")
            if user == "user:81684243-9356-4421-8fbf-a4f8d36aa31b":
                return mock_response('{"allowed": true, "resolution": "1234"}', 200)
            elif user == "user:81684243-9356-4421-8fbf-a4f8d36aa31c":
                return mock_response('{"allowed": false, "resolution": "1234"}', 200)
            elif user == "user:81684243-9356-4421-8fbf-a4f8d36aa31d":
                return mock_response('{"allowed": true, "resolution": "1234"}', 200)
            return mock_response('{"allowed": false, "resolution": "1234"}', 200)

        mock_request.side_effect = mock_side_effect
        configuration = self.configuration
        configuration.store_id = store_id
        async with OpenFgaClient(configuration) as api_client:
            api_response = await api_client.client_batch_check(
                body=[body1, body2, body3],
                options={
                    "authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1",
                    "max_parallel_requests": 2,
                },
            )
            self.assertIsInstance(api_response, list)
            self.assertEqual(len(api_response), 3)
            self.assertEqual(api_response[0].error, None)
            self.assertTrue(api_response[0].allowed)
            self.assertEqual(api_response[0].request, body1)
            self.assertEqual(api_response[1].error, None)
            self.assertFalse(api_response[1].allowed)
            self.assertEqual(api_response[1].request, body2)
            self.assertEqual(api_response[2].error, None)
            self.assertTrue(api_response[2].allowed)
            self.assertEqual(api_response[2].request, body3)
            # Make sure the API was called with the right data
            mock_request.assert_any_call(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/check",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "tuple_key": {
                        "object": "document:2021-budget",
                        "relation": "reader",
                        "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                    },
                    "authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )
            mock_request.assert_any_call(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/check",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "tuple_key": {
                        "object": "document:2021-budget",
                        "relation": "reader",
                        "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31c",
                    },
                    "authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )
            mock_request.assert_any_call(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/check",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "tuple_key": {
                        "object": "document:2021-budget",
                        "relation": "reader",
                        "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31d",
                    },
                    "authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )
            await api_client.close()

    @patch.object(rest.RESTClientObject, "request")
    async def test_client_batch_check_multiple_request_fail(self, mock_request):
        """Test case for check with multiple request with one request failed

        Check whether a user is authorized to access an object
        """
        response_body = """
{
  "code": "validation_error",
  "message": "Generic validation error"
}
        """

        body1 = ClientCheckRequest(
            object="document:2021-budget",
            relation="reader",
            user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
        )
        body2 = ClientCheckRequest(
            object="document:2021-budget",
            relation="reader",
            user="user:81684243-9356-4421-8fbf-a4f8d36aa31c",
        )
        body3 = ClientCheckRequest(
            object="document:2021-budget",
            relation="reader",
            user="user:81684243-9356-4421-8fbf-a4f8d36aa31d",
        )

        # Mock the response based on request body to avoid race conditions
        def mock_side_effect(*args, **kwargs):
            body = kwargs.get("body", {})
            user = body.get("tuple_key", {}).get("user", "")
            if user == "user:81684243-9356-4421-8fbf-a4f8d36aa31b":
                return mock_response('{"allowed": true, "resolution": "1234"}', 200)
            elif user == "user:81684243-9356-4421-8fbf-a4f8d36aa31c":
                raise ValidationException(
                    http_resp=http_mock_response(response_body, 400)
                )
            elif user == "user:81684243-9356-4421-8fbf-a4f8d36aa31d":
                return mock_response('{"allowed": false, "resolution": "1234"}', 200)
            return mock_response('{"allowed": false, "resolution": "1234"}', 200)

        mock_request.side_effect = mock_side_effect
        configuration = self.configuration
        configuration.store_id = store_id
        async with OpenFgaClient(configuration) as api_client:
            api_response = await api_client.client_batch_check(
                body=[body1, body2, body3],
                options={
                    "authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1",
                    "max_parallel_requests": 2,
                },
            )
            self.assertIsInstance(api_response, list)
            self.assertEqual(len(api_response), 3)
            self.assertEqual(api_response[0].error, None)
            self.assertTrue(api_response[0].allowed)
            self.assertEqual(api_response[0].request, body1)
            self.assertFalse(api_response[1].allowed)
            self.assertEqual(api_response[1].request, body2)
            self.assertIsInstance(api_response[1].error, ValidationException)
            self.assertIsInstance(
                api_response[1].error.parsed_exception, ValidationErrorMessageResponse
            )
            self.assertEqual(api_response[2].error, None)
            self.assertFalse(api_response[2].allowed)
            self.assertEqual(api_response[2].request, body3)
            # Make sure the API was called with the right data
            mock_request.assert_any_call(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/check",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "tuple_key": {
                        "object": "document:2021-budget",
                        "relation": "reader",
                        "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                    },
                    "authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )
            mock_request.assert_any_call(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/check",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "tuple_key": {
                        "object": "document:2021-budget",
                        "relation": "reader",
                        "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31c",
                    },
                    "authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )
            mock_request.assert_any_call(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/check",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "tuple_key": {
                        "object": "document:2021-budget",
                        "relation": "reader",
                        "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31d",
                    },
                    "authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )
            await api_client.close()

    @patch.object(rest.RESTClientObject, "request")
    async def test_batch_check_single_request(self, mock_request):
        """Test case for check with single request

        Check whether a user is authorized to access an object
        """

        # First, mock the response
        response_body = """
        {
            "result": {
                "1": {
                    "allowed": true
                }
            }
        }
        """
        mock_request.side_effect = [
            mock_response(response_body, 200),
        ]

        body = ClientBatchCheckRequest(
            checks=[
                ClientBatchCheckItem(
                    object="document:2021-budget",
                    relation="reader",
                    user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                    correlation_id="1",
                ),
            ]
        )
        configuration = self.configuration
        configuration.store_id = store_id
        async with OpenFgaClient(configuration) as api_client:
            api_response = await api_client.batch_check(
                body=body,
                options={"authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1"},
            )
            self.assertEqual(len(api_response.result), 1)
            self.assertEqual(api_response.result[0].error, None)
            self.assertTrue(api_response.result[0].allowed)
            self.assertEqual(api_response.result[0].correlation_id, "1")
            self.assertEqual(api_response.result[0].request, body.checks[0])
            # Make sure the API was called with the right data
            mock_request.assert_any_call(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/batch-check",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "checks": [
                        {
                            "tuple_key": {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                            },
                            "correlation_id": "1",
                        }
                    ],
                    "authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )
            await api_client.close()

    @patch.object(uuid, "uuid4")
    @patch.object(rest.RESTClientObject, "request")
    async def test_batch_check_multiple_request(self, mock_request, mock_uuid):
        """Test case for check with multiple request

        Check whether a user is authorized to access an object
        """
        first_response_body = """
        {
            "result": {
                "1": {
                    "allowed": true
                },
                "2": {
                    "allowed": false
                }
            }
        }
"""

        second_response_body = """
{
    "result": {
        "fake-uuid": {
            "error": {
                "input_error": "validation_error",
                "message": "type 'doc' not found"
            }
        }
    }
}"""

        # First, mock the response
        mock_request.side_effect = [
            mock_response(first_response_body, 200),
            mock_response(second_response_body, 200),
        ]

        def mock_v4(val: str):
            return val

        mock_uuid.side_effect = [mock_v4("batch-id-header"), mock_v4("fake-uuid")]

        body = ClientBatchCheckRequest(
            checks=[
                ClientBatchCheckItem(
                    object="document:2021-budget",
                    relation="reader",
                    user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                    correlation_id="1",
                ),
                ClientBatchCheckItem(
                    object="document:2021-budget",
                    relation="reader",
                    user="user:81684243-9356-4421-8fbf-a4f8d36aa31c",
                    correlation_id="2",
                ),
                ClientBatchCheckItem(
                    object="doc:2021-budget",
                    relation="reader",
                    user="user:81684243-9356-4421-8fbf-a4f8d36aa31d",
                ),
            ]
        )

        configuration = self.configuration
        configuration.store_id = store_id
        async with OpenFgaClient(configuration) as api_client:
            api_response = await api_client.batch_check(
                body=body,
                options={
                    "authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1",
                    "max_parallel_requests": 1,
                    "max_batch_size": 2,
                },
            )
            self.assertEqual(len(api_response.result), 3)
            self.assertEqual(api_response.result[0].error, None)
            self.assertTrue(api_response.result[0].allowed)
            self.assertEqual(api_response.result[1].error, None)
            self.assertFalse(api_response.result[1].allowed)
            self.assertEqual(
                api_response.result[2].error.message, "type 'doc' not found"
            )
            self.assertFalse(api_response.result[2].allowed)
            # value generated from the uuid mock
            self.assertEqual(api_response.result[2].correlation_id, "fake-uuid")
            # Make sure the API was called with the right data
            mock_request.assert_any_call(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/batch-check",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "checks": [
                        {
                            "tuple_key": {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                            },
                            "correlation_id": "1",
                        },
                        {
                            "tuple_key": {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31c",
                            },
                            "correlation_id": "2",
                        },
                    ],
                    "authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )
            mock_request.assert_any_call(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/batch-check",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "checks": [
                        {
                            "tuple_key": {
                                "object": "doc:2021-budget",
                                "relation": "reader",
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31d",
                            },
                            "correlation_id": "fake-uuid",
                        }
                    ],
                    "authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )
            await api_client.close()

    async def test_batch_check_errors_dupe_cor_id(self):
        """Test case for duplicate correlation_id being provided to batch_check"""

        body = ClientBatchCheckRequest(
            checks=[
                ClientBatchCheckItem(
                    object="document:2021-budget",
                    relation="reader",
                    user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                    correlation_id="1",
                ),
                ClientBatchCheckItem(
                    object="document:2021-budget",
                    relation="reader",
                    user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                    correlation_id="1",
                ),
            ]
        )
        configuration = self.configuration
        configuration.store_id = store_id
        async with OpenFgaClient(configuration) as api_client:
            with self.assertRaises(FgaValidationException) as error:
                await api_client.batch_check(
                    body=body,
                    options={"authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1"},
                )
            self.assertEqual(
                "Duplicate correlation_id (1) provided", str(error.exception)
            )
            await api_client.close()

    @patch.object(rest.RESTClientObject, "request")
    async def test_batch_check_errors_unauthorized(self, mock_request):
        """Test case for BatchCheck with a 401"""
        first_response_body = """
        {
            "result": {
                "1": {
                    "allowed": true
                },
                "2": {
                    "allowed": false
                }
            }
        }
"""

        # First, mock the response
        mock_request.side_effect = [
            mock_response(first_response_body, 200),
            UnauthorizedException(http_resp=http_mock_response("{}", 401)),
        ]

        body = ClientBatchCheckRequest(
            checks=[
                ClientBatchCheckItem(
                    object="document:2021-budget",
                    relation="reader",
                    user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                    correlation_id="1",
                ),
                ClientBatchCheckItem(
                    object="document:2021-budget",
                    relation="reader",
                    user="user:81684243-9356-4421-8fbf-a4f8d36aa31c",
                    correlation_id="2",
                ),
                ClientBatchCheckItem(
                    object="document:2021-budget",
                    relation="reader",
                    user="user:81684243-9356-4421-8fbf-a4f8d36aa31d",
                    correlation_id="3",
                ),
            ]
        )

        configuration = self.configuration
        configuration.store_id = store_id
        async with OpenFgaClient(configuration) as api_client:
            with self.assertRaises(UnauthorizedException):
                await api_client.batch_check(
                    body=body,
                    options={
                        "authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1",
                        "max_parallel_requests": 1,
                        "max_batch_size": 2,
                    },
                )

            # Make sure the API was called with the right data
            mock_request.assert_any_call(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/batch-check",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "checks": [
                        {
                            "tuple_key": {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                            },
                            "correlation_id": "1",
                        },
                        {
                            "tuple_key": {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31c",
                            },
                            "correlation_id": "2",
                        },
                    ],
                    "authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )
            mock_request.assert_any_call(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/batch-check",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "checks": [
                        {
                            "tuple_key": {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31d",
                            },
                            "correlation_id": "3",
                        }
                    ],
                    "authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )
            await api_client.close()

    @patch.object(rest.RESTClientObject, "request")
    async def test_expand(self, mock_request):
        """Test case for expand

        Expand all relationships in userset tree format, and following userset rewrite rules.  Useful to reason about and debug a certain relationship
        """
        response_body = """{
            "tree": {"root": {"name": "document:budget#reader", "leaf": {"users": {"users": ["user:81684243-9356-4421-8fbf-a4f8d36aa31b"]}}}}}
            """
        mock_request.return_value = mock_response(response_body, 200)
        configuration = self.configuration
        configuration.store_id = store_id
        async with OpenFgaClient(configuration) as api_client:
            body = ClientExpandRequest(
                object="document:budget",
                relation="reader",
            )
            api_response = await api_client.expand(
                body=body,
                options={
                    "authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1",
                    "consistency": ConsistencyPreference.MINIMIZE_LATENCY,
                },
            )
            self.assertIsInstance(api_response, ExpandResponse)
            cur_users = Users(users=["user:81684243-9356-4421-8fbf-a4f8d36aa31b"])
            leaf = Leaf(users=cur_users)
            node = Node(name="document:budget#reader", leaf=leaf)
            userTree = UsersetTree(node)
            expected_response = ExpandResponse(userTree)
            self.assertEqual(api_response, expected_response)
            mock_request.assert_called_once_with(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/expand",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "tuple_key": {"object": "document:budget", "relation": "reader"},
                    "authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1",
                    "consistency": "MINIMIZE_LATENCY",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )
            await api_client.close()

    @patch.object(rest.RESTClientObject, "request")
    async def test_list_objects(self, mock_request):
        """Test case for list_objects

        List objects
        """
        response_body = """
{
  "objects": [
    "document:abcd1234"
  ]
}
            """
        mock_request.return_value = mock_response(response_body, 200)
        configuration = self.configuration
        configuration.store_id = store_id
        async with OpenFgaClient(configuration) as api_client:
            body = ClientListObjectsRequest(
                type="document",
                relation="reader",
                user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
            )
            # Get all stores
            api_response = await api_client.list_objects(
                body,
                options={
                    "authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1",
                    "consistency": ConsistencyPreference.MINIMIZE_LATENCY,
                },
            )
            self.assertIsInstance(api_response, ListObjectsResponse)
            self.assertEqual(api_response.objects, ["document:abcd1234"])
            mock_request.assert_called_once_with(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/list-objects",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1",
                    "type": "document",
                    "relation": "reader",
                    "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                    "consistency": "MINIMIZE_LATENCY",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )
            await api_client.close()

    @patch.object(rest.RESTClientObject, "request")
    async def test_list_objects_contextual_tuples(self, mock_request):
        """Test case for list_objects

        List objects
        """
        response_body = """
{
  "objects": [
    "document:abcd1234"
  ]
}
            """
        mock_request.return_value = mock_response(response_body, 200)
        configuration = self.configuration
        configuration.store_id = store_id
        async with OpenFgaClient(configuration) as api_client:
            body = ClientListObjectsRequest(
                type="document",
                relation="reader",
                user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                contextual_tuples=[
                    ClientTuple(
                        user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                        relation="writer",
                        object="document:budget",
                    ),
                ],
            )
            # Get all stores
            api_response = await api_client.list_objects(
                body, options={"authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1"}
            )
            self.assertIsInstance(api_response, ListObjectsResponse)
            self.assertEqual(api_response.objects, ["document:abcd1234"])
            mock_request.assert_called_once_with(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/list-objects",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1",
                    "type": "document",
                    "relation": "reader",
                    "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                    "contextual_tuples": {
                        "tuple_keys": [
                            {
                                "object": "document:budget",
                                "relation": "writer",
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                            }
                        ]
                    },
                },
                _preload_content=ANY,
                _request_timeout=None,
            )
            await api_client.close()

    @patch.object(rest.RESTClientObject, "request")
    async def test_list_relations(self, mock_request):
        """Test case for list relations

        Check whether a user is authorized to access an object
        """

        def mock_check_requests(*args, **kwargs):
            body = kwargs.get("body")
            tuple_key = body.get("tuple_key")
            if tuple_key["relation"] == "owner":
                return mock_response('{"allowed": false, "resolution": "1234"}', 200)
            return mock_response('{"allowed": true, "resolution": "1234"}', 200)

        # First, mock the response
        mock_request.side_effect = mock_check_requests

        configuration = self.configuration
        configuration.store_id = store_id
        async with OpenFgaClient(configuration) as api_client:
            api_response = await api_client.list_relations(
                body=ClientListRelationsRequest(
                    user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                    relations=["reader", "owner", "viewer"],
                    object="document:2021-budget",
                ),
                options={
                    "authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1",
                    "consistency": ConsistencyPreference.MINIMIZE_LATENCY,
                },
            )
            self.assertEqual(api_response, ["reader", "viewer"])

            # Make sure the API was called with the right data
            mock_request.assert_any_call(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/check",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "tuple_key": {
                        "object": "document:2021-budget",
                        "relation": "reader",
                        "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                    },
                    "authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1",
                    "consistency": "MINIMIZE_LATENCY",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )
            mock_request.assert_any_call(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/check",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "tuple_key": {
                        "object": "document:2021-budget",
                        "relation": "owner",
                        "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                    },
                    "authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1",
                    "consistency": "MINIMIZE_LATENCY",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )
            mock_request.assert_any_call(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/check",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "tuple_key": {
                        "object": "document:2021-budget",
                        "relation": "viewer",
                        "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                    },
                    "authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1",
                    "consistency": "MINIMIZE_LATENCY",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )
            await api_client.close()

    @patch.object(rest.RESTClientObject, "request")
    async def test_list_relations_unauthorized(self, mock_request):
        """Test case for list relations with 401 response"""

        mock_request.side_effect = UnauthorizedException(
            http_resp=http_mock_response("{}", 401)
        )
        configuration = self.configuration
        configuration.store_id = store_id
        async with OpenFgaClient(configuration) as api_client:
            with self.assertRaises(UnauthorizedException):
                await api_client.list_relations(
                    body=ClientListRelationsRequest(
                        user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                        relations=["reader", "owner", "viewer"],
                        object="document:2021-budget",
                    ),
                    options={"authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1"},
                )

            mock_request.assert_called()
            await api_client.close()

    @patch.object(rest.RESTClientObject, "request")
    async def test_list_relations_errored(self, mock_request):
        """Test case for list relations with undefined exception"""

        mock_request.side_effect = ValueError()
        configuration = self.configuration
        configuration.store_id = store_id
        async with OpenFgaClient(configuration) as api_client:
            with self.assertRaises(ValueError):
                await api_client.list_relations(
                    body=ClientListRelationsRequest(
                        user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                        relations=["reader", "owner", "viewer"],
                        object="document:2021-budget",
                    ),
                    options={"authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1"},
                )

            mock_request.assert_called()
            await api_client.close()

    @patch.object(rest.RESTClientObject, "request")
    async def test_list_users(self, mock_request):
        """
        Test case for list_users
        """

        response_body = """{
  "users": [
    {
      "object": {
        "id": "81684243-9356-4421-8fbf-a4f8d36aa31b",
        "type": "user"
      }
    },
    {
      "userset": {
        "id": "fga",
        "relation": "member",
        "type": "team"
      }
    },
    {
      "wildcard": {
        "type": "user"
      }
    }
  ]
}"""

        mock_request.return_value = mock_response(response_body, 200)

        configuration = self.configuration
        configuration.store_id = store_id

        async with OpenFgaClient(configuration) as api_client:
            body = ClientListUsersRequest(
                object=FgaObject(type="document", id="2021-budget"),
                relation="can_read",
                user_filters=[
                    UserTypeFilter(type="user"),
                ],
                context={},
                contextual_tuples=[
                    ClientTuple(
                        user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                        relation="editor",
                        object="folder:product",
                    ),
                    ClientTuple(
                        user="folder:product",
                        relation="parent",
                        object="document:0192ab2a-d83f-756d-9397-c5ed9f3cb69a",
                    ),
                ],
            )

            response = await api_client.list_users(
                body,
                options={
                    "authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J",
                    "consistency": ConsistencyPreference.MINIMIZE_LATENCY,
                },
            )

            self.assertIsInstance(response, ListUsersResponse)

            self.assertEqual(response.users.__len__(), 3)

            self.assertIsNotNone(response.users[0].object)
            self.assertEqual(
                response.users[0].object.id, "81684243-9356-4421-8fbf-a4f8d36aa31b"
            )
            self.assertEqual(response.users[0].object.type, "user")
            self.assertIsNone(response.users[0].userset)
            self.assertIsNone(response.users[0].wildcard)

            self.assertIsNone(response.users[1].object)
            self.assertIsNotNone(response.users[1].userset)
            self.assertEqual(response.users[1].userset.id, "fga")
            self.assertEqual(response.users[1].userset.relation, "member")
            self.assertEqual(response.users[1].userset.type, "team")
            self.assertIsNone(response.users[1].wildcard)

            self.assertIsNone(response.users[2].object)
            self.assertIsNone(response.users[2].userset)
            self.assertIsNotNone(response.users[2].wildcard)
            self.assertEqual(response.users[2].wildcard.type, "user")

            mock_request.assert_called_once_with(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/list-users",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J",
                    "object": {"id": "2021-budget", "type": "document"},
                    "relation": "can_read",
                    "user_filters": [
                        {"type": "user"},
                    ],
                    "contextual_tuples": [
                        {
                            "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                            "relation": "editor",
                            "object": "folder:product",
                        },
                        {
                            "user": "folder:product",
                            "relation": "parent",
                            "object": "document:0192ab2a-d83f-756d-9397-c5ed9f3cb69a",
                        },
                    ],
                    "context": {},
                    "consistency": "MINIMIZE_LATENCY",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )

            await api_client.close()

    @patch.object(rest.RESTClientObject, "request")
    async def test_read_assertions(self, mock_request):
        """Test case for read assertions"""
        response_body = """
{
  "authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J",
  "assertions": [
    {
      "tuple_key": {
        "object": "document:2021-budget",
        "relation": "reader",
        "user": "user:anne"
      },
      "expectation": true
    }
  ]
}
        """
        mock_request.return_value = mock_response(response_body, 200)
        configuration = self.configuration
        configuration.store_id = store_id
        # Enter a context with an instance of the API client
        async with OpenFgaClient(configuration) as api_client:
            api_response = await api_client.read_assertions(
                options={"authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J"}
            )
            self.assertEqual(
                api_response,
                ReadAssertionsResponse(
                    authorization_model_id="01G5JAVJ41T49E9TT3SKVS7X1J",
                    assertions=[
                        Assertion(
                            tuple_key=TupleKeyWithoutCondition(
                                object="document:2021-budget",
                                relation="reader",
                                user="user:anne",
                            ),
                            expectation=True,
                        )
                    ],
                ),
            )
            mock_request.assert_called_once_with(
                "GET",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/assertions/01G5JAVJ41T49E9TT3SKVS7X1J",
                headers=ANY,
                body=None,
                query_params=[],
                post_params=[],
                _preload_content=ANY,
                _request_timeout=None,
            )

    @patch.object(rest.RESTClientObject, "request")
    async def test_write_assertions(self, mock_request):
        """Test case for write assertions

        Get all stores
        """
        mock_request.return_value = mock_response("", 204)
        configuration = self.configuration
        configuration.store_id = store_id
        async with OpenFgaClient(configuration) as api_client:
            await api_client.write_assertions(
                [
                    ClientAssertion(
                        user="user:anne",
                        relation="reader",
                        object="document:2021-budget",
                        expectation=True,
                    )
                ],
                options={"authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J"},
            )
            mock_request.assert_called_once_with(
                "PUT",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/assertions/01G5JAVJ41T49E9TT3SKVS7X1J",
                headers=ANY,
                body={
                    "assertions": [
                        {
                            "tuple_key": {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:anne",
                            },
                            "expectation": True,
                        }
                    ]
                },
                query_params=[],
                post_params=[],
                _preload_content=ANY,
                _request_timeout=None,
            )

    @patch.object(rest.RESTClientObject, "request")
    async def test_set_store_id(self, mock_request):
        """Test case for write assertions

        Get all stores
        """
        mock_request.return_value = mock_response("", 204)
        configuration = self.configuration
        configuration.store_id = store_id
        async with OpenFgaClient(configuration) as api_client:
            api_client.set_store_id("01YCP46JKYM8FJCQ37NMBYHE5Y")

            await api_client.write_assertions(
                [
                    ClientAssertion(
                        user="user:anne",
                        relation="reader",
                        object="document:2021-budget",
                        expectation=True,
                    )
                ],
                options={"authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J"},
            )
            self.assertEqual(api_client.get_store_id(), "01YCP46JKYM8FJCQ37NMBYHE5Y")
            mock_request.assert_called_once_with(
                "PUT",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5Y/assertions/01G5JAVJ41T49E9TT3SKVS7X1J",
                headers=ANY,
                body={
                    "assertions": [
                        {
                            "tuple_key": {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:anne",
                            },
                            "expectation": True,
                        }
                    ]
                },
                query_params=[],
                post_params=[],
                _preload_content=ANY,
                _request_timeout=None,
            )

    @patch.object(rest.RESTClientObject, "request")
    async def test_config_auth_model(self, mock_request):
        """Test case for write assertions

        Get all stores
        """
        mock_request.return_value = mock_response("", 204)
        configuration = self.configuration
        configuration.store_id = store_id
        configuration.authorization_model_id = "01G5JAVJ41T49E9TT3SKVS7X1J"
        async with OpenFgaClient(configuration) as api_client:
            await api_client.write_assertions(
                [
                    ClientAssertion(
                        user="user:anne",
                        relation="reader",
                        object="document:2021-budget",
                        expectation=True,
                    )
                ],
                options={},
            )
            self.assertEqual(
                api_client.get_authorization_model_id(), "01G5JAVJ41T49E9TT3SKVS7X1J"
            )
            mock_request.assert_called_once_with(
                "PUT",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/assertions/01G5JAVJ41T49E9TT3SKVS7X1J",
                headers=ANY,
                body={
                    "assertions": [
                        {
                            "tuple_key": {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:anne",
                            },
                            "expectation": True,
                        }
                    ]
                },
                query_params=[],
                post_params=[],
                _preload_content=ANY,
                _request_timeout=None,
            )

    @patch.object(rest.RESTClientObject, "request")
    async def test_update_auth_model(self, mock_request):
        """Test case for write assertions

        Get all stores
        """
        mock_request.return_value = mock_response("", 204)
        configuration = self.configuration
        configuration.store_id = store_id
        configuration.authorization_model_id = "01G5JAVJ41T49E9TT3SKVS7X1J"
        async with OpenFgaClient(configuration) as api_client:
            api_client.set_authorization_model_id("01G5JAVJ41T49E9TT3SKVS7X2J")

            await api_client.write_assertions(
                [
                    ClientAssertion(
                        user="user:anne",
                        relation="reader",
                        object="document:2021-budget",
                        expectation=True,
                    )
                ],
                options={},
            )
            mock_request.assert_called_once_with(
                "PUT",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/assertions/01G5JAVJ41T49E9TT3SKVS7X2J",
                headers=ANY,
                body={
                    "assertions": [
                        {
                            "tuple_key": {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:anne",
                            },
                            "expectation": True,
                        }
                    ]
                },
                query_params=[],
                post_params=[],
                _preload_content=ANY,
                _request_timeout=None,
            )

    def test_configuration_store_id_invalid(self):
        """
        Test whether ApiValueError is raised if host has query
        """
        configuration = ClientConfiguration(
            api_host="localhost", api_scheme="http", store_id="abcd"
        )
        self.assertRaises(FgaValidationException, configuration.is_valid)

    def test_configuration_authorization_model_id_invalid(self):
        """
        Test whether ApiValueError is raised if host has query
        """
        configuration = ClientConfiguration(
            api_host="localhost",
            api_scheme="http",
            store_id="01H15K9J85050XTEDPVM8DJM78",
            authorization_model_id="abcd",
        )
        self.assertRaises(FgaValidationException, configuration.is_valid)

    def test_set_heading_if_not_set_when_none_provided(self):
        """Should set header when no options provided"""
        result = set_heading_if_not_set(None, "X-Test-Header", "default-value")

        self.assertIsNotNone(result)
        self.assertIn("headers", result)
        self.assertEqual(result["headers"]["X-Test-Header"], "default-value")

    def test_set_heading_if_not_set_when_empty_options_provided(self):
        """Should set header when empty options dict provided"""
        result = set_heading_if_not_set({}, "X-Test-Header", "default-value")

        self.assertIn("headers", result)
        self.assertEqual(result["headers"]["X-Test-Header"], "default-value")

    def test_set_heading_if_not_set_when_no_headers_in_options(self):
        """Should set header when options dict has no headers key"""
        options = {"page_size": 10}
        result = set_heading_if_not_set(options, "X-Test-Header", "default-value")

        self.assertIn("headers", result)
        self.assertEqual(result["headers"]["X-Test-Header"], "default-value")
        self.assertEqual(result["page_size"], 10)

    def test_set_heading_if_not_set_when_headers_empty(self):
        """Should set header when headers dict is empty"""
        options = {"headers": {}}
        result = set_heading_if_not_set(options, "X-Test-Header", "default-value")

        self.assertEqual(result["headers"]["X-Test-Header"], "default-value")

    def test_set_heading_if_not_set_does_not_override_existing_custom_header(self):
        """Should NOT override when custom header already exists - this is the critical test for the bug fix"""
        options = {"headers": {"X-Test-Header": "custom-value"}}
        result = set_heading_if_not_set(options, "X-Test-Header", "default-value")

        # Custom header should be preserved, NOT overridden by default
        self.assertEqual(result["headers"]["X-Test-Header"], "custom-value")

    def test_set_heading_if_not_set_preserves_other_headers_when_setting_new_header(
        self,
    ):
        """Should preserve existing headers when setting a new one"""
        options = {"headers": {"X-Existing-Header": "existing-value"}}
        result = set_heading_if_not_set(options, "X-New-Header", "new-value")

        self.assertEqual(result["headers"]["X-Existing-Header"], "existing-value")
        self.assertEqual(result["headers"]["X-New-Header"], "new-value")

    def test_set_heading_if_not_set_handles_integer_header_values(self):
        """Should not override existing integer header values"""
        options = {"headers": {"X-Retry-Count": 5}}
        result = set_heading_if_not_set(options, "X-Retry-Count", 1)

        # Existing integer value should be preserved
        self.assertEqual(result["headers"]["X-Retry-Count"], 5)

    def test_set_heading_if_not_set_handles_non_dict_headers_value(self):
        """Should convert non-dict headers value to dict"""
        options = {"headers": "invalid"}
        result = set_heading_if_not_set(options, "X-Test-Header", "default-value")

        self.assertIsInstance(result["headers"], dict)
        self.assertEqual(result["headers"]["X-Test-Header"], "default-value")

    def test_set_heading_if_not_set_does_not_mutate_when_header_exists(self):
        """Should return same dict when header already exists"""
        options = {"headers": {"X-Test-Header": "custom-value"}}
        original_value = options["headers"]["X-Test-Header"]

        result = set_heading_if_not_set(options, "X-Test-Header", "default-value")

        # Should return the same modified dict
        self.assertIs(result, options)
        # Value should not have changed
        self.assertEqual(result["headers"]["X-Test-Header"], original_value)

    def test_set_heading_if_not_set_multiple_headers_with_mixed_states(self):
        """Should handle multiple headers, some existing and some new"""
        options = {
            "headers": {
                "X-Custom-Header": "custom-value",
                "X-Another-Header": "another-value",
            }
        }

        # Try to set a custom header (should not override)
        result = set_heading_if_not_set(options, "X-Custom-Header", "default-value")
        self.assertEqual(result["headers"]["X-Custom-Header"], "custom-value")

        # Try to set a new header (should be added)
        result = set_heading_if_not_set(result, "X-New-Header", "new-value")
        self.assertEqual(result["headers"]["X-New-Header"], "new-value")

        # Original headers should still exist
        self.assertEqual(result["headers"]["X-Another-Header"], "another-value")

    def test_set_heading_if_not_set_two_defaults_two_customs_one_override(self):
        """Test setting two default headers when two custom headers exist, with one custom overriding one default"""
        # Start with two custom headers
        options = {
            "headers": {
                "X-Request-ID": "my-custom-request-id",  # This should override the default
                "X-Tenant-ID": "tenant-123",  # This is custom-only
            }
        }

        # Try to set two default headers
        result = set_heading_if_not_set(options, "X-SDK-Version", "1.0.0")
        result = set_heading_if_not_set(result, "X-Request-ID", "default-uuid")

        # Verify all four headers exist with correct values
        self.assertEqual(result["headers"]["X-SDK-Version"], "1.0.0")  # Default was set
        self.assertEqual(
            result["headers"]["X-Request-ID"], "my-custom-request-id"
        )  # Custom overrode default
        self.assertEqual(
            result["headers"]["X-Tenant-ID"], "tenant-123"
        )  # Custom preserved
        self.assertEqual(len(result["headers"]), 3)  # Exactly 3 headers

    def test_set_heading_if_not_set_with_empty_string_value(self):
        """Test that empty string values in custom headers are preserved and not overridden."""
        options = {"headers": {"X-Custom-Header": ""}}
        result = set_heading_if_not_set(options, "X-Custom-Header", "default-value")
        self.assertEqual(result["headers"]["X-Custom-Header"], "")

    def test_set_heading_if_not_set_with_unicode_characters(self):
        """Test that headers with Unicode characters are handled correctly."""
        options = {"headers": {"X-Custom-Header": "日本語"}}
        result = set_heading_if_not_set(options, "X-Custom-Header", "default-value")
        self.assertEqual(result["headers"]["X-Custom-Header"], "日本語")

        # Test setting a new header with Unicode
        result = set_heading_if_not_set({}, "X-Unicode-Header", "🔒")
        self.assertEqual(result["headers"]["X-Unicode-Header"], "🔒")

    def test_set_heading_if_not_set_with_special_characters(self):
        """Test that headers with special characters are handled correctly."""
        options = {"headers": {"X-Custom-Header": "value-with-special!@#$%^&*()_+"}}
        result = set_heading_if_not_set(options, "X-Custom-Header", "default")
        self.assertEqual(
            result["headers"]["X-Custom-Header"], "value-with-special!@#$%^&*()_+"
        )

    def test_set_heading_if_not_set_case_sensitivity(self):
        """Test that header names are treated as case-sensitive by the helper function."""
        options = {"headers": {"x-custom-header": "lowercase"}}
        result = set_heading_if_not_set(options, "X-Custom-Header", "uppercase")
        self.assertEqual(result["headers"]["X-Custom-Header"], "uppercase")
        self.assertEqual(result["headers"]["x-custom-header"], "lowercase")

    @patch.object(rest.RESTClientObject, "request")
    async def test_content_type_cannot_be_overridden_by_custom_headers(
        self, mock_request
    ):
        """Test that Content-Type header cannot be overridden by custom headers."""
        response_body = '{"allowed": true, "resolution": "1234"}'
        mock_request.return_value = mock_response(response_body, 200)

        body = ClientCheckRequest(
            object="document:2021-budget",
            relation="reader",
            user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
        )

        configuration = self.configuration
        configuration.store_id = store_id
        configuration.authorization_model_id = "01GXSA8YR785C4FYS3C0RTG7B1"

        async with OpenFgaClient(configuration) as api_client:
            # Try to override Content-Type with a custom value
            custom_options = {"headers": {"Content-Type": "text/plain"}}
            await api_client.check(body=body, options=custom_options)

            call_args = mock_request.call_args
            headers = call_args[1]["headers"]

            # Content-Type should be application/json, NOT the custom text/plain
            self.assertEqual(headers.get("Content-Type"), "application/json")
            self.assertNotEqual(headers.get("Content-Type"), "text/plain")

    @patch.object(rest.RESTClientObject, "request")
    async def test_check_with_custom_headers_override_defaults(self, mock_request):
        """Test that custom headers in options override default headers for check API."""
        response_body = '{"allowed": true, "resolution": "1234"}'
        mock_request.return_value = mock_response(response_body, 200)

        body = ClientCheckRequest(
            object="document:2021-budget",
            relation="reader",
            user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
        )

        configuration = self.configuration
        configuration.store_id = store_id
        configuration.authorization_model_id = "01GXSA8YR785C4FYS3C0RTG7B1"

        async with OpenFgaClient(configuration) as api_client:
            custom_options = {"headers": {"X-Custom-Request-Id": "custom-request-123"}}
            api_response = await api_client.check(body=body, options=custom_options)

            call_args = mock_request.call_args
            headers = call_args[1]["headers"]
            self.assertEqual(headers.get("X-Custom-Request-Id"), "custom-request-123")
            self.assertIsInstance(api_response, CheckResponse)

    @patch.object(rest.RESTClientObject, "request")
    async def test_write_with_custom_headers(self, mock_request):
        """Test that custom headers work correctly with write API."""
        response_body = '{"writes": [], "deletes": []}'
        mock_request.return_value = mock_response(response_body, 200)

        body = ClientWriteRequest(
            writes=[
                ClientTuple(
                    object="document:budget",
                    relation="reader",
                    user="user:anne",
                )
            ]
        )

        configuration = self.configuration
        configuration.store_id = store_id

        async with OpenFgaClient(configuration) as api_client:
            custom_options = {
                "headers": {"X-Trace-Id": "trace-xyz-789"},
                "authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1",
            }
            await api_client.write(body=body, options=custom_options)

            call_args = mock_request.call_args
            headers = call_args[1]["headers"]
            self.assertEqual(headers.get("X-Trace-Id"), "trace-xyz-789")

    @patch.object(rest.RESTClientObject, "request")
    async def test_expand_with_custom_headers(self, mock_request):
        """Test that custom headers are passed correctly in expand API calls."""
        response_body = '{"tree": {"root": {"name": "document:1#viewer", "leaf": {"users": {"users": ["user:anne"]}}}}}'
        mock_request.return_value = mock_response(response_body, 200)

        body = ClientExpandRequest(
            object="document:1",
            relation="viewer",
        )

        configuration = self.configuration
        configuration.store_id = store_id
        configuration.authorization_model_id = "01GXSA8YR785C4FYS3C0RTG7B1"

        async with OpenFgaClient(configuration) as api_client:
            custom_options = {"headers": {"X-Expand-Id": "expand-456"}}
            api_response = await api_client.expand(body=body, options=custom_options)

            call_args = mock_request.call_args
            headers = call_args[1]["headers"]
            self.assertEqual(headers.get("X-Expand-Id"), "expand-456")
            self.assertIsInstance(api_response, ExpandResponse)

    @patch.object(rest.RESTClientObject, "request")
    async def test_list_objects_with_custom_headers(self, mock_request):
        """Test that custom headers are passed correctly in list_objects API calls."""
        response_body = '{"objects": ["document:1", "document:2"]}'
        mock_request.return_value = mock_response(response_body, 200)

        body = ClientListObjectsRequest(
            type="document",
            relation="viewer",
            user="user:anne",
        )

        configuration = self.configuration
        configuration.store_id = store_id
        configuration.authorization_model_id = "01GXSA8YR785C4FYS3C0RTG7B1"

        async with OpenFgaClient(configuration) as api_client:
            custom_options = {"headers": {"X-List-Objects-Id": "list-obj-999"}}
            api_response = await api_client.list_objects(
                body=body, options=custom_options
            )

            call_args = mock_request.call_args
            headers = call_args[1]["headers"]
            self.assertEqual(headers.get("X-List-Objects-Id"), "list-obj-999")
            self.assertIsInstance(api_response, ListObjectsResponse)

    @patch.object(rest.RESTClientObject, "request")
    async def test_list_users_with_custom_headers(self, mock_request):
        """Test that custom headers are passed correctly in list_users API calls."""
        response_body = '{"users": [{"object": {"type": "user", "id": "anne"}}, {"object": {"type": "user", "id": "bob"}}]}'
        mock_request.return_value = mock_response(response_body, 200)

        body = ClientListUsersRequest(
            object=FgaObject(type="document", id="1"),
            relation="viewer",
            user_filters=[{"type": "user"}],
        )

        configuration = self.configuration
        configuration.store_id = store_id
        configuration.authorization_model_id = "01GXSA8YR785C4FYS3C0RTG7B1"

        async with OpenFgaClient(configuration) as api_client:
            custom_options = {"headers": {"X-List-Users-Id": "list-users-777"}}
            api_response = await api_client.list_users(
                body=body, options=custom_options
            )

            call_args = mock_request.call_args
            headers = call_args[1]["headers"]
            self.assertEqual(headers.get("X-List-Users-Id"), "list-users-777")
            self.assertIsInstance(api_response, ListUsersResponse)

    @patch.object(rest.RESTClientObject, "request")
    async def test_multiple_api_calls_with_different_custom_headers(self, mock_request):
        """Test that different custom headers can be used for different API calls."""

        def mock_side_effect(*args, **kwargs):
            path = args[1]
            if "check" in path:
                return mock_response('{"allowed": true, "resolution": "1234"}', 200)
            elif "expand" in path:
                return mock_response(
                    '{"tree": {"root": {"name": "document:1#viewer", "leaf": {"users": {"users": ["user:anne"]}}}}}',
                    200,
                )
            return mock_response("{}", 200)

        mock_request.side_effect = mock_side_effect

        check_body = ClientCheckRequest(
            object="document:2021-budget",
            relation="reader",
            user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
        )

        expand_body = ClientExpandRequest(
            object="document:1",
            relation="viewer",
        )

        configuration = self.configuration
        configuration.store_id = store_id
        configuration.authorization_model_id = "01GXSA8YR785C4FYS3C0RTG7B1"

        async with OpenFgaClient(configuration) as api_client:
            # First call with custom header 1
            check_options = {"headers": {"X-Request-Id": "check-request-111"}}
            check_response = await api_client.check(
                body=check_body, options=check_options
            )

            # Second call with custom header 2
            expand_options = {"headers": {"X-Request-Id": "expand-request-222"}}
            expand_response = await api_client.expand(
                body=expand_body, options=expand_options
            )

            # Verify first call had correct header
            first_call_args = mock_request.call_args_list[0]
            first_headers = first_call_args[1]["headers"]
            self.assertEqual(first_headers.get("X-Request-Id"), "check-request-111")

            # Verify second call had correct header
            second_call_args = mock_request.call_args_list[1]
            second_headers = second_call_args[1]["headers"]
            self.assertEqual(second_headers.get("X-Request-Id"), "expand-request-222")

            self.assertIsInstance(check_response, CheckResponse)
            self.assertIsInstance(expand_response, ExpandResponse)

    @patch.object(rest.RESTClientObject, "request")
    async def test_client_batch_check_with_custom_headers(self, mock_request):
        """Test that custom headers work correctly in batch check operations."""

        def mock_side_effect(*args, **kwargs):
            body = kwargs.get("body", {})
            user = body.get("tuple_key", {}).get("user", "")
            if user == "user:anne":
                return mock_response('{"allowed": true, "resolution": "1234"}', 200)
            elif user == "user:bob":
                return mock_response('{"allowed": false, "resolution": "5678"}', 200)
            return mock_response('{"allowed": false, "resolution": "0000"}', 200)

        mock_request.side_effect = mock_side_effect

        body = [
            ClientCheckRequest(
                object="document:budget",
                relation="reader",
                user="user:anne",
            ),
            ClientCheckRequest(
                object="document:roadmap",
                relation="writer",
                user="user:bob",
            ),
        ]

        configuration = self.configuration
        configuration.store_id = store_id

        async with OpenFgaClient(configuration) as api_client:
            custom_options = {
                "headers": {"X-Batch-Id": "batch-xyz-123"},
                "authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1",
            }
            api_response = await api_client.client_batch_check(
                body=body, options=custom_options
            )

            # Verify all calls had the custom header
            for call_args in mock_request.call_args_list:
                headers = call_args[1]["headers"]
                self.assertEqual(headers.get("X-Batch-Id"), "batch-xyz-123")

            self.assertEqual(len(api_response), 2)
            self.assertTrue(api_response[0].allowed)
            self.assertFalse(api_response[1].allowed)

    async def test_client_initialization_without_headers(self):
        """Test that client initializes correctly without headers"""
        config = ClientConfiguration(
            api_url="https://api.fga.example",
            store_id="01ARZ3NDEKTSV4RRFFQ69G5FAV",
        )

        async with OpenFgaClient(config) as client:
            # Should not raise any errors
            assert client._client_configuration == config
            assert "User-Agent" in client._api_client.default_headers

    async def test_client_initialization_with_headers(self):
        """Test that client applies headers from configuration on initialization"""
        headers = {
            "X-Custom-Header": "custom-value",
            "X-Request-Source": "test-app",
        }
        config = ClientConfiguration(
            api_url="https://api.fga.example",
            store_id="01ARZ3NDEKTSV4RRFFQ69G5FAV",
            headers=headers,
        )

        async with OpenFgaClient(config) as client:
            # Verify headers were set on the API client
            assert "X-Custom-Header" in client._api_client.default_headers
            assert (
                client._api_client.default_headers["X-Custom-Header"] == "custom-value"
            )
            assert "X-Request-Source" in client._api_client.default_headers
            assert client._api_client.default_headers["X-Request-Source"] == "test-app"

    async def test_client_initialization_with_empty_headers(self):
        """Test client initialization with empty headers dict"""
        config = ClientConfiguration(
            api_url="https://api.fga.example",
            store_id="01ARZ3NDEKTSV4RRFFQ69G5FAV",
            headers={},
        )

        async with OpenFgaClient(config) as client:
            # Only default User-Agent header should be present
            assert "User-Agent" in client._api_client.default_headers
            # No custom headers should be set
            assert (
                len(
                    [k for k in client._api_client.default_headers if k != "User-Agent"]
                )
                == 0
            )

    async def test_client_initialization_with_multiple_headers(self):
        """Test client initialization with multiple custom headers"""
        headers = {
            "X-Request-ID": "123e4567-e89b-12d3-a456-426614174000",
            "X-API-Key": "secret-key",
            "X-Tenant-ID": "tenant-123",
            "X-User-Agent": "custom-agent/1.0",
        }
        config = ClientConfiguration(
            api_url="https://api.fga.example",
            store_id="01ARZ3NDEKTSV4RRFFQ69G5FAV",
            headers=headers,
        )

        async with OpenFgaClient(config) as client:
            for header_name, header_value in headers.items():
                assert header_name in client._api_client.default_headers
                assert client._api_client.default_headers[header_name] == header_value

    async def test_client_initialization_headers_with_none(self):
        """Test client initialization with headers=None"""
        config = ClientConfiguration(
            api_url="https://api.fga.example",
            store_id="01ARZ3NDEKTSV4RRFFQ69G5FAV",
            headers=None,
        )

        async with OpenFgaClient(config) as client:
            # Should only have default User-Agent header
            assert "User-Agent" in client._api_client.default_headers

    async def test_correlation_id_tracking(self):
        """Test using headers for correlation ID tracking"""
        config = ClientConfiguration(
            api_url="https://api.fga.example",
            store_id="01ARZ3NDEKTSV4RRFFQ69G5FAV",
            headers={
                "X-Correlation-ID": "correlation-123",
                "X-Request-Source": "api-gateway",
            },
        )

        async with OpenFgaClient(config) as client:
            assert (
                client._api_client.default_headers["X-Correlation-ID"]
                == "correlation-123"
            )
            assert (
                client._api_client.default_headers["X-Request-Source"] == "api-gateway"
            )

    async def test_api_versioning_headers(self):
        """Test using headers for API versioning"""
        config = ClientConfiguration(
            api_url="https://api.fga.example",
            store_id="01ARZ3NDEKTSV4RRFFQ69G5FAV",
            headers={
                "X-API-Version": "2024-01-01",
                "Accept": "application/vnd.openfga.v1+json",
            },
        )

        async with OpenFgaClient(config) as client:
            assert client._api_client.default_headers["X-API-Version"] == "2024-01-01"
            assert (
                client._api_client.default_headers["Accept"]
                == "application/vnd.openfga.v1+json"
            )

    async def test_multi_tenant_headers(self):
        """Test using headers for multi-tenant applications"""
        config = ClientConfiguration(
            api_url="https://api.fga.example",
            store_id="01ARZ3NDEKTSV4RRFFQ69G5FAV",
            headers={
                "X-Tenant-ID": "tenant-abc-123",
                "X-Organization-ID": "org-xyz-789",
                "X-Environment": "production",
            },
        )

        async with OpenFgaClient(config) as client:
            assert client._api_client.default_headers["X-Tenant-ID"] == "tenant-abc-123"
            assert (
                client._api_client.default_headers["X-Organization-ID"] == "org-xyz-789"
            )
            assert client._api_client.default_headers["X-Environment"] == "production"

    async def test_authentication_delegation_headers(self):
        """Test using headers for authentication delegation"""
        config = ClientConfiguration(
            api_url="https://api.fga.example",
            store_id="01ARZ3NDEKTSV4RRFFQ69G5FAV",
            headers={
                "X-Forwarded-User": "user@example.com",
                "X-Forwarded-Groups": "admin,developers",
            },
        )

        async with OpenFgaClient(config) as client:
            assert (
                client._api_client.default_headers["X-Forwarded-User"]
                == "user@example.com"
            )
            assert (
                client._api_client.default_headers["X-Forwarded-Groups"]
                == "admin,developers"
            )

    async def test_custom_user_agent(self):
        """Test setting custom User-Agent header"""
        config = ClientConfiguration(
            api_url="https://api.fga.example",
            store_id="01ARZ3NDEKTSV4RRFFQ69G5FAV",
            headers={
                "User-Agent": "MyApp/1.0 (custom-client)",
            },
        )

        async with OpenFgaClient(config) as client:
            # Custom User-Agent should override the default
            assert "MyApp/1.0" in client._api_client.default_headers["User-Agent"]


@pytest.fixture
def client_configuration():
    """Fixture for creating a basic ClientConfiguration"""
    return ClientConfiguration(
        api_url="https://api.fga.example",
        store_id="01ARZ3NDEKTSV4RRFFQ69G5FAV",
    )


class TestClientConfigurationHeaders:
    """Tests for ClientConfiguration headers parameter"""

    def test_client_configuration_headers_default_none(self, client_configuration):
        """Test that headers default to an empty dict in ClientConfiguration"""
        assert client_configuration.headers == {}

    def test_client_configuration_headers_initialization_with_dict(self):
        """Test initializing ClientConfiguration with headers"""
        headers = {
            "X-Custom-Header": "custom-value",
            "X-Request-Source": "test-app",
        }
        config = ClientConfiguration(
            api_url="https://api.fga.example",
            store_id="01ARZ3NDEKTSV4RRFFQ69G5FAV",
            headers=headers,
        )
        assert config.headers == headers
        assert config.headers["X-Custom-Header"] == "custom-value"
        assert config.headers["X-Request-Source"] == "test-app"

    def test_client_configuration_headers_initialization_with_none(self):
        """Test initializing ClientConfiguration with headers=None"""
        config = ClientConfiguration(
            api_url="https://api.fga.example",
            headers=None,
        )
        assert config.headers == {}

    def test_client_configuration_headers_setter(self, client_configuration):
        """Test setting headers via property setter"""
        headers = {"X-Test": "test-value"}
        client_configuration.headers = headers
        assert client_configuration.headers == headers

    def test_client_configuration_headers_with_authorization_model_id(self):
        """Test ClientConfiguration with headers and authorization_model_id"""
        headers = {"X-Model": "test"}
        config = ClientConfiguration(
            api_url="https://api.fga.example",
            store_id="01ARZ3NDEKTSV4RRFFQ69G5FAV",
            authorization_model_id="01ARZ3NDEKTSV4RRFFQ69G5FAV",
            headers=headers,
        )
        assert config.headers == headers
        assert config.authorization_model_id == "01ARZ3NDEKTSV4RRFFQ69G5FAV"

    def test_client_configuration_headers_deepcopy(self):
        """Test that headers are properly deep copied in ClientConfiguration"""
        headers = {"X-Test": "value"}
        config = ClientConfiguration(
            api_url="https://api.fga.example",
            store_id="01ARZ3NDEKTSV4RRFFQ69G5FAV",
            headers=headers,
        )

        copied_config = copy.deepcopy(config)

        assert copied_config.headers == config.headers
        assert copied_config.headers is not config.headers

        config.headers["X-New"] = "new-value"
        assert "X-New" not in copied_config.headers

    @patch.object(rest.RESTClientObject, "request")
    @pytest.mark.asyncio
    async def test_write_with_conflict_options_ignore_duplicates(self, mock_request):
        """Test case for write with conflict options - ignore duplicates"""
        from openfga_sdk.client.models.write_conflict_opts import (
            ClientWriteRequestOnDuplicateWrites,
            ConflictOptions,
        )

        response_body = "{}"
        mock_request.return_value = mock_response(response_body, 200)
        self.configuration = ClientConfiguration(
            api_url="http://api.fga.example",
        )
        configuration = self.configuration
        configuration.store_id = store_id
        async with OpenFgaClient(configuration) as api_client:
            body = ClientWriteRequest(
                writes=[
                    ClientTuple(
                        object="document:2021-budget",
                        relation="reader",
                        user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                    ),
                ],
            )
            await api_client.write(
                body,
                options={
                    "authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J",
                    "conflict": ConflictOptions(
                        on_duplicate_writes=ClientWriteRequestOnDuplicateWrites.IGNORE
                    ),
                },
            )
            mock_request.assert_called_once_with(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/write",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "writes": {
                        "tuple_keys": [
                            {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                            },
                        ],
                        "on_duplicate": "ignore",
                    },
                    "authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )

    @patch.object(rest.RESTClientObject, "request")
    @pytest.mark.asyncio
    async def test_write_with_conflict_options_ignore_missing_deletes(
        self, mock_request
    ):
        """Test case for write with conflict options - ignore missing deletes"""
        from openfga_sdk.client.models.write_conflict_opts import (
            ClientWriteRequestOnMissingDeletes,
            ConflictOptions,
        )

        response_body = "{}"
        mock_request.return_value = mock_response(response_body, 200)
        self.configuration = ClientConfiguration(
            api_url="http://api.fga.example",
        )
        configuration = self.configuration
        configuration.store_id = store_id
        async with OpenFgaClient(configuration) as api_client:
            body = ClientWriteRequest(
                deletes=[
                    ClientTuple(
                        object="document:2021-budget",
                        relation="reader",
                        user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                    )
                ],
            )
            await api_client.write(
                body,
                options={
                    "authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J",
                    "conflict": ConflictOptions(
                        on_missing_deletes=ClientWriteRequestOnMissingDeletes.IGNORE
                    ),
                },
            )
            mock_request.assert_called_once_with(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/write",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "deletes": {
                        "tuple_keys": [
                            {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                            },
                        ],
                        "on_missing": "ignore",
                    },
                    "authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )

    @patch.object(rest.RESTClientObject, "request")
    @pytest.mark.asyncio
    async def test_write_with_conflict_options_both(self, mock_request):
        """Test case for write with both conflict options"""
        from openfga_sdk.client.models.write_conflict_opts import (
            ClientWriteRequestOnDuplicateWrites,
            ClientWriteRequestOnMissingDeletes,
            ConflictOptions,
        )

        response_body = "{}"
        mock_request.return_value = mock_response(response_body, 200)
        self.configuration = ClientConfiguration(
            api_url="http://api.fga.example",
        )
        configuration = self.configuration
        configuration.store_id = store_id
        async with OpenFgaClient(configuration) as api_client:
            body = ClientWriteRequest(
                writes=[
                    ClientTuple(
                        object="document:2021-budget",
                        relation="reader",
                        user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                    ),
                ],
                deletes=[
                    ClientTuple(
                        object="document:2021-report",
                        relation="reader",
                        user="user:81684243-9356-4421-8fbf-a4f8d36aa31c",
                    )
                ],
            )
            await api_client.write(
                body,
                options={
                    "authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J",
                    "conflict": ConflictOptions(
                        on_duplicate_writes=ClientWriteRequestOnDuplicateWrites.IGNORE,
                        on_missing_deletes=ClientWriteRequestOnMissingDeletes.IGNORE,
                    ),
                },
            )
            mock_request.assert_called_once_with(
                "POST",
                "http://api.fga.example/stores/01YCP46JKYM8FJCQ37NMBYHE5X/write",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "writes": {
                        "tuple_keys": [
                            {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                            },
                        ],
                        "on_duplicate": "ignore",
                    },
                    "deletes": {
                        "tuple_keys": [
                            {
                                "object": "document:2021-report",
                                "relation": "reader",
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31c",
                            },
                        ],
                        "on_missing": "ignore",
                    },
                    "authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )
