import unittest

from datetime import datetime, timedelta, timezone
from unittest import IsolatedAsyncioTestCase
from unittest.mock import ANY, patch

import urllib3

import openfga_sdk

from openfga_sdk import rest
from openfga_sdk.api import open_fga_api
from openfga_sdk.constants import USER_AGENT
from openfga_sdk.credentials import CredentialConfiguration, Credentials
from openfga_sdk.exceptions import (
    FGA_REQUEST_ID,
    ApiValueError,
    FgaValidationException,
    NotFoundException,
    RateLimitExceededError,
    ServiceException,
    ValidationException,
)
from openfga_sdk.models.assertion import Assertion
from openfga_sdk.models.authorization_model import AuthorizationModel
from openfga_sdk.models.check_request import CheckRequest
from openfga_sdk.models.check_response import CheckResponse
from openfga_sdk.models.create_store_request import CreateStoreRequest
from openfga_sdk.models.create_store_response import CreateStoreResponse
from openfga_sdk.models.error_code import ErrorCode
from openfga_sdk.models.expand_request import ExpandRequest
from openfga_sdk.models.expand_request_tuple_key import ExpandRequestTupleKey
from openfga_sdk.models.expand_response import ExpandResponse
from openfga_sdk.models.get_store_response import GetStoreResponse
from openfga_sdk.models.internal_error_code import InternalErrorCode
from openfga_sdk.models.internal_error_message_response import (
    InternalErrorMessageResponse,
)
from openfga_sdk.models.leaf import Leaf
from openfga_sdk.models.list_objects_request import ListObjectsRequest
from openfga_sdk.models.list_objects_response import ListObjectsResponse
from openfga_sdk.models.list_stores_response import ListStoresResponse
from openfga_sdk.models.list_users_request import ListUsersRequest
from openfga_sdk.models.list_users_response import ListUsersResponse
from openfga_sdk.models.node import Node
from openfga_sdk.models.not_found_error_code import NotFoundErrorCode
from openfga_sdk.models.object_relation import ObjectRelation
from openfga_sdk.models.path_unknown_error_message_response import (
    PathUnknownErrorMessageResponse,
)
from openfga_sdk.models.read_assertions_response import ReadAssertionsResponse
from openfga_sdk.models.read_authorization_model_response import (
    ReadAuthorizationModelResponse,
)
from openfga_sdk.models.read_changes_response import ReadChangesResponse
from openfga_sdk.models.read_request import ReadRequest
from openfga_sdk.models.read_request_tuple_key import ReadRequestTupleKey
from openfga_sdk.models.read_response import ReadResponse
from openfga_sdk.models.store import Store
from openfga_sdk.models.tuple import Tuple
from openfga_sdk.models.tuple_change import TupleChange
from openfga_sdk.models.tuple_key import TupleKey
from openfga_sdk.models.tuple_key_without_condition import TupleKeyWithoutCondition
from openfga_sdk.models.tuple_operation import TupleOperation
from openfga_sdk.models.type_definition import TypeDefinition
from openfga_sdk.models.users import Users
from openfga_sdk.models.userset import Userset
from openfga_sdk.models.userset_tree import UsersetTree
from openfga_sdk.models.usersets import Usersets
from openfga_sdk.models.validation_error_message_response import (
    ValidationErrorMessageResponse,
)
from openfga_sdk.models.write_assertions_request import WriteAssertionsRequest
from openfga_sdk.models.write_authorization_model_request import (
    WriteAuthorizationModelRequest,
)
from openfga_sdk.models.write_authorization_model_response import (
    WriteAuthorizationModelResponse,
)
from openfga_sdk.models.write_request import WriteRequest
from openfga_sdk.models.write_request_deletes import WriteRequestDeletes
from openfga_sdk.models.write_request_writes import WriteRequestWrites


store_id = "01H0H015178Y2V4CX10C2KGHF4"
request_id = "x1y2z3"


# Helper function to construct mock response
def http_mock_response(body, status, headers=None):
    if headers is None:
        headers = {}

    default_headers = urllib3.response.HTTPHeaderDict(
        {"content-type": "application/json", "Fga-Request-Id": request_id}
    )

    headers = {**default_headers, **headers}

    return urllib3.HTTPResponse(
        body.encode("utf-8"), headers, status, preload_content=False
    )


def mock_response(body, status):
    obj = http_mock_response(body, status)
    return rest.RESTResponse(obj, obj.data)


class TestOpenFgaApi(IsolatedAsyncioTestCase):
    """OpenFgaApi unit test stubs"""

    def setUp(self):
        self.configuration = openfga_sdk.Configuration(
            api_url="http://api.fga.example",
        )

    def tearDown(self):
        pass

    @patch.object(rest.RESTClientObject, "request")
    async def test_check(self, mock_request):
        """Test case for check

        Check whether a user is authorized to access an object
        """

        # First, mock the response
        response_body = '{"allowed": true, "resolution": "1234"}'
        mock_request.return_value = mock_response(response_body, 200)

        configuration = self.configuration
        configuration.store_id = store_id
        async with openfga_sdk.ApiClient(configuration) as api_client:
            api_instance = open_fga_api.OpenFgaApi(api_client)
            body = CheckRequest(
                tuple_key=TupleKey(
                    object="document:2021-budget",
                    relation="reader",
                    user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                ),
                authorization_model_id="01GXSA8YR785C4FYS3C0RTG7B1",
            )
            api_response = await api_instance.check(
                body=body,
            )
            self.assertIsInstance(api_response, CheckResponse)
            self.assertTrue(api_response.allowed)
            # Make sure the API was called with the right data
            mock_request.assert_called_once_with(
                "POST",
                "http://api.fga.example/stores/01H0H015178Y2V4CX10C2KGHF4/check",
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
        async with openfga_sdk.ApiClient(configuration) as api_client:
            api_instance = open_fga_api.OpenFgaApi(api_client)
            body = CreateStoreRequest(
                name="test-store",
            )
            api_response = await api_instance.create_store(
                body=body,
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
    async def test_delete_store(self, mock_request):
        """Test case for delete_store

        Delete a store
        """
        response_body = ""
        mock_request.return_value = mock_response(response_body, 201)
        configuration = self.configuration
        configuration.store_id = store_id
        async with openfga_sdk.ApiClient(configuration) as api_client:
            api_instance = open_fga_api.OpenFgaApi(api_client)
            await api_instance.delete_store()
            mock_request.assert_called_once_with(
                "DELETE",
                "http://api.fga.example/stores/01H0H015178Y2V4CX10C2KGHF4",
                headers=ANY,
                body=None,
                query_params=[],
                post_params=[],
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
        async with openfga_sdk.ApiClient(configuration) as api_client:
            api_instance = open_fga_api.OpenFgaApi(api_client)
            body = ExpandRequest(
                tuple_key=ExpandRequestTupleKey(
                    object="document:budget",
                    relation="reader",
                ),
                authorization_model_id="01GXSA8YR785C4FYS3C0RTG7B1",
            )
            api_response = await api_instance.expand(
                body=body,
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
                "http://api.fga.example/stores/01H0H015178Y2V4CX10C2KGHF4/expand",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "tuple_key": {"object": "document:budget", "relation": "reader"},
                    "authorization_model_id": "01GXSA8YR785C4FYS3C0RTG7B1",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )
            await api_client.close()

    @patch.object(rest.RESTClientObject, "request")
    async def test_get_store(self, mock_request):
        """Test case for get_store

        Get a store
        """
        response_body = """{
  "id": "01H0H015178Y2V4CX10C2KGHF4",
  "name": "test_store",
  "created_at": "2022-07-25T20:45:10.485Z",
  "updated_at": "2022-07-25T20:45:10.485Z"
}
            """
        mock_request.return_value = mock_response(response_body, 200)
        configuration = self.configuration
        configuration.store_id = store_id
        async with openfga_sdk.ApiClient(configuration) as api_client:
            api_instance = open_fga_api.OpenFgaApi(api_client)
            # Get a store
            api_response = await api_instance.get_store()
            self.assertIsInstance(api_response, GetStoreResponse)
            self.assertEqual(api_response.id, "01H0H015178Y2V4CX10C2KGHF4")
            self.assertEqual(api_response.name, "test_store")
            mock_request.assert_called_once_with(
                "GET",
                "http://api.fga.example/stores/01H0H015178Y2V4CX10C2KGHF4",
                headers=ANY,
                body=None,
                query_params=[],
                post_params=[],
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
        async with openfga_sdk.ApiClient(configuration) as api_client:
            api_instance = open_fga_api.OpenFgaApi(api_client)
            body = ListObjectsRequest(
                authorization_model_id="01G5JAVJ41T49E9TT3SKVS7X1J",
                type="document",
                relation="reader",
                user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
            )
            # Get all stores
            api_response = await api_instance.list_objects(body)
            self.assertIsInstance(api_response, ListObjectsResponse)
            self.assertEqual(api_response.objects, ["document:abcd1234"])
            mock_request.assert_called_once_with(
                "POST",
                "http://api.fga.example/stores/01H0H015178Y2V4CX10C2KGHF4/list-objects",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J",
                    "type": "document",
                    "relation": "reader",
                    "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                },
                _preload_content=ANY,
                _request_timeout=None,
            )
            await api_client.close()

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
        async with openfga_sdk.ApiClient(configuration) as api_client:
            api_instance = open_fga_api.OpenFgaApi(api_client)
            # Get all stores
            api_response = await api_instance.list_stores(
                page_size=1,
                continuation_token="continuation_token_example",
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

        async with openfga_sdk.ApiClient(configuration) as api_client:
            api_instance = open_fga_api.OpenFgaApi(api_client)

            request = ListUsersRequest(
                authorization_model_id="01G5JAVJ41T49E9TT3SKVS7X1J",
                object="document:2021-budget",
                relation="can_read",
                user_filters=[
                    {"type": "user"},
                ],
                context={},
                contextual_tuples=[
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
            )

            response = await api_instance.list_users(request)

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
                "http://api.fga.example/stores/01H0H015178Y2V4CX10C2KGHF4/list-users",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J",
                    "object": "document:2021-budget",
                    "relation": "can_read",
                    "user_filters": [
                        {"type": "user"},
                    ],
                    "context": {},
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
                },
                _preload_content=ANY,
                _request_timeout=None,
            )

            await api_client.close()

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
        async with openfga_sdk.ApiClient(configuration) as api_client:
            api_instance = open_fga_api.OpenFgaApi(api_client)
            body = ReadRequest(
                tuple_key=ReadRequestTupleKey(
                    object="document:2021-budget",
                    relation="reader",
                    user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                ),
                page_size=50,
                continuation_token="eyJwayI6IkxBVEVTVF9OU0NPTkZJR19hdXRoMHN0b3JlIiwic2siOiIxem1qbXF3MWZLZExTcUoyN01MdTdqTjh0cWgifQ==",
            )
            api_response = await api_instance.read(
                body=body,
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
                "http://api.fga.example/stores/01H0H015178Y2V4CX10C2KGHF4/read",
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
                },
                _preload_content=ANY,
                _request_timeout=None,
            )

    @patch.object(rest.RESTClientObject, "request")
    async def test_read_assertions(self, mock_request):
        """Test case for read_assertions

        Read assertions for an authorization model ID
        """
        response_body = """
{
  "authorization_model_id": "01G5JAVJ41T49E9TT3SKVS7X1J",
  "assertions": [
    {
      "tuple_key": {
        "object": "document:2021-budget",
        "relation": "reader",
        "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b"
      },
      "expectation": true
    }
  ]
}
        """
        mock_request.return_value = mock_response(response_body, 200)
        configuration = self.configuration
        configuration.store_id = store_id
        async with openfga_sdk.ApiClient(configuration) as api_client:
            api_instance = open_fga_api.OpenFgaApi(api_client)
            api_response = await api_instance.read_assertions(
                "01G5JAVJ41T49E9TT3SKVS7X1J",
            )
            self.assertIsInstance(api_response, ReadAssertionsResponse)
            self.assertEqual(
                api_response.authorization_model_id, "01G5JAVJ41T49E9TT3SKVS7X1J"
            )
            assertion = Assertion(
                tuple_key=TupleKeyWithoutCondition(
                    object="document:2021-budget",
                    relation="reader",
                    user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                ),
                expectation=True,
            )
            self.assertEqual(api_response.assertions, [assertion])
            mock_request.assert_called_once_with(
                "GET",
                "http://api.fga.example/stores/01H0H015178Y2V4CX10C2KGHF4/assertions/01G5JAVJ41T49E9TT3SKVS7X1J",
                headers=ANY,
                body=None,
                query_params=[],
                post_params=[],
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
        async with openfga_sdk.ApiClient(configuration) as api_client:
            # Create an instance of the API class
            api_instance = open_fga_api.OpenFgaApi(api_client)

            # Return a particular version of an authorization model
            api_response = await api_instance.read_authorization_model(
                "01G5JAVJ41T49E9TT3SKVS7X1J",
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
                "http://api.fga.example/stores/01H0H015178Y2V4CX10C2KGHF4/authorization-models/01G5JAVJ41T49E9TT3SKVS7X1J",
                headers=ANY,
                body=None,
                query_params=[],
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
        async with openfga_sdk.ApiClient(configuration) as api_client:
            # Create an instance of the API class
            api_instance = open_fga_api.OpenFgaApi(api_client)

            # Return a particular version of an authorization model
            api_response = await api_instance.read_changes(
                page_size=1,
                continuation_token="abcdefg",
                start_time="2022-01-01T00:00:00+00:00",
                type="document",
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
                "http://api.fga.example/stores/01H0H015178Y2V4CX10C2KGHF4/changes",
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
    async def test_write(self, mock_request):
        """Test case for write

        Add tuples from the store
        """
        response_body = "{}"
        mock_request.return_value = mock_response(response_body, 200)
        configuration = self.configuration
        configuration.store_id = store_id
        # Enter a context with an instance of the API client
        async with openfga_sdk.ApiClient(configuration) as api_client:
            # Create an instance of the API class
            api_instance = open_fga_api.OpenFgaApi(api_client)

            # example passing only required values which don't have defaults set

            body = WriteRequest(
                writes=WriteRequestWrites(
                    tuple_keys=[
                        TupleKey(
                            object="document:2021-budget",
                            relation="reader",
                            user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                        )
                    ],
                ),
                authorization_model_id="01G5JAVJ41T49E9TT3SKVS7X1J",
            )
            await api_instance.write(
                body,
            )
            mock_request.assert_called_once_with(
                "POST",
                "http://api.fga.example/stores/01H0H015178Y2V4CX10C2KGHF4/write",
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

    @patch.object(rest.RESTClientObject, "request")
    async def test_write_delete(self, mock_request):
        """Test case for write

        Delete tuples from the store
        """
        response_body = "{}"
        mock_request.return_value = mock_response(response_body, 200)
        configuration = self.configuration
        configuration.store_id = store_id
        # Enter a context with an instance of the API client
        async with openfga_sdk.ApiClient(configuration) as api_client:
            # Create an instance of the API class
            api_instance = open_fga_api.OpenFgaApi(api_client)

            # example passing only required values which don't have defaults set

            body = WriteRequest(
                deletes=WriteRequestDeletes(
                    tuple_keys=[
                        TupleKey(
                            object="document:2021-budget",
                            relation="reader",
                            user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                        )
                    ],
                ),
                authorization_model_id="01G5JAVJ41T49E9TT3SKVS7X1J",
            )
            await api_instance.write(
                body,
            )
            mock_request.assert_called_once_with(
                "POST",
                "http://api.fga.example/stores/01H0H015178Y2V4CX10C2KGHF4/write",
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
    async def test_write_assertions(self, mock_request):
        """Test case for write_assertions

        Upsert assertions for an authorization model ID
        """
        response_body = ""
        mock_request.return_value = mock_response(response_body, 204)
        configuration = self.configuration
        configuration.store_id = store_id
        # Enter a context with an instance of the API client
        async with openfga_sdk.ApiClient(configuration) as api_client:
            # Create an instance of the API class
            api_instance = open_fga_api.OpenFgaApi(api_client)

            # example passing only required values which don't have defaults set
            body = WriteAssertionsRequest(
                assertions=[
                    Assertion(
                        tuple_key=TupleKey(
                            object="document:2021-budget",
                            relation="reader",
                            user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                        ),
                        expectation=True,
                    )
                ],
            )
            # Upsert assertions for an authorization model ID
            await api_instance.write_assertions(
                authorization_model_id="xyz0123",
                body=body,
            )
            mock_request.assert_called_once_with(
                "PUT",
                "http://api.fga.example/stores/01H0H015178Y2V4CX10C2KGHF4/assertions/xyz0123",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "assertions": [
                        {
                            "expectation": True,
                            "tuple_key": {
                                "object": "document:2021-budget",
                                "relation": "reader",
                                "user": "user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                            },
                        }
                    ]
                },
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
        async with openfga_sdk.ApiClient(configuration) as api_client:
            # Create an instance of the API class
            api_instance = open_fga_api.OpenFgaApi(api_client)

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
            api_response = await api_instance.write_authorization_model(body)
            self.assertIsInstance(api_response, WriteAuthorizationModelResponse)
            expected_response = WriteAuthorizationModelResponse(
                authorization_model_id="01G5JAVJ41T49E9TT3SKVS7X1J"
            )
            self.assertEqual(api_response, expected_response)
            mock_request.assert_called_once_with(
                "POST",
                "http://api.fga.example/stores/01H0H015178Y2V4CX10C2KGHF4/authorization-models",
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

    def test_default_scheme(self):
        """
        Ensure default scheme is https
        """
        configuration = openfga_sdk.Configuration(api_host="localhost")
        self.assertEqual(configuration.api_scheme, "https")

    def test_host_port(self):
        """
        Ensure host has port will not raise error
        """
        configuration = openfga_sdk.Configuration(api_host="localhost:3000")
        self.assertEqual(configuration.api_host, "localhost:3000")

    def test_configuration_missing_host(self):
        """
        Test whether FgaValidationException is raised if configuration does not have host specified
        """
        configuration = openfga_sdk.Configuration(api_scheme="http")
        self.assertRaises(FgaValidationException, configuration.is_valid)

    def test_configuration_missing_scheme(self):
        """
        Test whether FgaValidationException is raised if configuration does not have scheme specified
        """
        configuration = openfga_sdk.Configuration(api_host="localhost")
        configuration.api_scheme = None
        self.assertRaises(FgaValidationException, configuration.is_valid)

    def test_configuration_bad_scheme(self):
        """
        Test whether ApiValueError is raised if scheme is bad
        """
        configuration = openfga_sdk.Configuration(
            api_host="localhost", api_scheme="foo"
        )
        self.assertRaises(ApiValueError, configuration.is_valid)

    def test_configuration_bad_host(self):
        """
        Test whether ApiValueError is raised if host is bad
        """
        configuration = openfga_sdk.Configuration(api_host="/", api_scheme="foo")
        self.assertRaises(ApiValueError, configuration.is_valid)

    def test_configuration_has_path(self):
        """
        Test whether ApiValueError is raised if host has path
        """
        configuration = openfga_sdk.Configuration(
            api_host="localhost/mypath", api_scheme="http"
        )
        self.assertRaises(ApiValueError, configuration.is_valid)

    def test_configuration_has_query(self):
        """
        Test whether ApiValueError is raised if host has query
        """
        configuration = openfga_sdk.Configuration(
            api_host="localhost?mypath=foo", api_scheme="http"
        )
        self.assertRaises(ApiValueError, configuration.is_valid)

    def test_configuration_store_id_invalid(self):
        """
        Test whether ApiValueError is raised if host has query
        """
        configuration = openfga_sdk.Configuration(
            api_host="localhost", api_scheme="http", store_id="abcd"
        )
        self.assertRaises(FgaValidationException, configuration.is_valid)

    def test_url(self):
        """
        Ensure that api_url is set and validated
        """
        configuration = openfga_sdk.Configuration(api_url="http://localhost:8080")
        self.assertEqual(configuration.api_url, "http://localhost:8080")
        configuration.is_valid()

    def test_url_with_scheme_and_host(self):
        """
        Ensure that api_url takes precedence over api_host and scheme
        """
        configuration = openfga_sdk.Configuration(
            api_url="http://localhost:8080", api_host="localhost:8080", api_scheme="foo"
        )
        self.assertEqual(configuration.api_url, "http://localhost:8080")
        configuration.is_valid()  # Should not throw and complain about scheme being invalid

    def test_timeout_millisec(self):
        """
        Ensure that timeout_seconds is set and validated
        """
        configuration = openfga_sdk.Configuration(
            api_url="http://localhost:8080",
            timeout_millisec=10000,
        )
        self.assertEqual(configuration.timeout_millisec, 10000)
        configuration.is_valid()

    async def test_bad_configuration_read_authorization_model(self):
        """
        Test whether FgaValidationException is raised for API (reading authorization models)
        with configuration is having incorrect API scheme
        """
        configuration = openfga_sdk.Configuration(
            api_scheme="bad",
            api_host="api.fga.example",
        )
        configuration.store_id = "xyz123"
        # Enter a context with an instance of the API client
        async with openfga_sdk.ApiClient(configuration) as api_client:
            # Create an instance of the API class
            api_instance = open_fga_api.OpenFgaApi(api_client)

            # expects FgaValidationException to be thrown because api_scheme is bad
            with self.assertRaises(ApiValueError):
                await api_instance.read_authorization_models(
                    page_size=1, continuation_token="abcdefg"
                )

    async def test_configuration_missing_storeid(self):
        """
        Test whether FgaValidationException is raised for API (reading authorization models)
        required store ID but configuration is missing store ID
        """
        configuration = openfga_sdk.Configuration(
            api_scheme="http",
            api_host="api.fga.example",
        )
        # Notice the store_id is not set
        # Enter a context with an instance of the API client
        async with openfga_sdk.ApiClient(configuration) as api_client:
            # Create an instance of the API class
            api_instance = open_fga_api.OpenFgaApi(api_client)

            # expects FgaValidationException to be thrown because store_id is not specified
            with self.assertRaises(FgaValidationException):
                await api_instance.read_authorization_models(
                    page_size=1, continuation_token="abcdefg"
                )

    @patch.object(rest.RESTClientObject, "request")
    async def test_400_error(self, mock_request):
        """
        Test to ensure 400 errors are handled properly
        """
        response_body = """
{
  "code": "validation_error",
  "message": "Generic validation error"
}
        """
        mock_request.side_effect = ValidationException(
            http_resp=http_mock_response(response_body, 400)
        )

        configuration = self.configuration
        configuration.store_id = store_id
        async with openfga_sdk.ApiClient(configuration) as api_client:
            api_instance = open_fga_api.OpenFgaApi(api_client)
            body = CheckRequest(
                tuple_key=TupleKey(
                    object="document:2021-budget",
                    relation="reader",
                    user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                ),
            )
            with self.assertRaises(ValidationException) as api_exception:
                await api_instance.check(
                    body=body,
                )
            self.assertIsInstance(
                api_exception.exception.parsed_exception, ValidationErrorMessageResponse
            )
            self.assertEqual(
                api_exception.exception.parsed_exception.code,
                ErrorCode.VALIDATION_ERROR,
            )
            self.assertEqual(
                api_exception.exception.parsed_exception.message,
                "Generic validation error",
            )
            self.assertEqual(
                api_exception.exception.header.get(FGA_REQUEST_ID), request_id
            )

    @patch.object(rest.RESTClientObject, "request")
    async def test_404_error(self, mock_request):
        """
        Test to ensure 404 errors are handled properly
        """
        response_body = """
{
  "code": "undefined_endpoint",
  "message": "Endpoint not enabled"
}
        """
        mock_request.side_effect = NotFoundException(
            http_resp=http_mock_response(response_body, 404)
        )

        configuration = self.configuration
        configuration.store_id = store_id
        async with openfga_sdk.ApiClient(configuration) as api_client:
            api_instance = open_fga_api.OpenFgaApi(api_client)
            body = CheckRequest(
                tuple_key=TupleKey(
                    object="document:2021-budget",
                    relation="reader",
                    user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                ),
            )
            with self.assertRaises(NotFoundException) as api_exception:
                await api_instance.check(
                    body=body,
                )
            self.assertIsInstance(
                api_exception.exception.parsed_exception,
                PathUnknownErrorMessageResponse,
            )
            self.assertEqual(
                api_exception.exception.parsed_exception.code,
                NotFoundErrorCode.UNDEFINED_ENDPOINT,
            )
            self.assertEqual(
                api_exception.exception.parsed_exception.message, "Endpoint not enabled"
            )

    @patch.object(rest.RESTClientObject, "request")
    async def test_429_error_no_retry(self, mock_request):
        """
        Test to ensure 429 errors are handled properly.
        For this case, there is no retry configured
        """
        response_body = """
{
  "code": "rate_limit_exceeded",
  "message": "Rate Limit exceeded"
}
        """
        mock_request.side_effect = RateLimitExceededError(
            http_resp=http_mock_response(response_body, 429)
        )

        retry = openfga_sdk.configuration.RetryParams(0, 10)
        configuration = self.configuration
        configuration.store_id = store_id
        configuration.retry_params = retry
        async with openfga_sdk.ApiClient(configuration) as api_client:
            api_instance = open_fga_api.OpenFgaApi(api_client)
            body = CheckRequest(
                tuple_key=TupleKey(
                    object="document:2021-budget",
                    relation="reader",
                    user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                ),
            )
            with self.assertRaises(RateLimitExceededError) as api_exception:
                await api_instance.check(
                    body=body,
                )
            self.assertIsInstance(api_exception.exception, RateLimitExceededError)
            mock_request.assert_called()
            self.assertEqual(mock_request.call_count, 1)

    @patch.object(rest.RESTClientObject, "request")
    async def test_429_error_first_error(self, mock_request):
        """
        Test to ensure 429 errors are handled properly.
        For this case, retry is configured and only the first time has error
        """
        response_body = '{"allowed": true, "resolution": "1234"}'
        error_response_body = """
{
  "code": "rate_limit_exceeded",
  "message": "Rate Limit exceeded"
}
        """
        mock_request.side_effect = [
            RateLimitExceededError(
                http_resp=http_mock_response(error_response_body, 429)
            ),
            mock_response(response_body, 200),
        ]

        retry = openfga_sdk.configuration.RetryParams(1, 10)
        configuration = self.configuration
        configuration.store_id = store_id
        configuration.retry_params = retry
        async with openfga_sdk.ApiClient(configuration) as api_client:
            api_instance = open_fga_api.OpenFgaApi(api_client)
            body = CheckRequest(
                tuple_key=TupleKey(
                    object="document:2021-budget",
                    relation="reader",
                    user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                ),
            )
            api_response = await api_instance.check(
                body=body,
            )
            self.assertIsInstance(api_response, CheckResponse)
            self.assertTrue(api_response.allowed)
            mock_request.assert_called()
            self.assertEqual(mock_request.call_count, 2)

    @patch("asyncio.sleep")
    @patch.object(rest.RESTClientObject, "request")
    async def test_429_error_retry_exponential_backoff(self, mock_request, mock_sleep):
        """
        Test to ensure 429 errors are handled properly.
        For this case, retry is configured but no Retry-After header is provided.
        Should default to exponential backoff with an upper limit.
        """
        response_body = '{"allowed": true, "resolution": "1234"}'
        error_response_body = """
                {
                  "code": "rate_limit_exceeded",
                  "message": "Rate Limit exceeded"
                }
        """
        mock_request.side_effect = [
            RateLimitExceededError(
                http_resp=http_mock_response(error_response_body, 429)
            ),
            RateLimitExceededError(
                http_resp=http_mock_response(error_response_body, 429)
            ),
            RateLimitExceededError(
                http_resp=http_mock_response(error_response_body, 429)
            ),
            RateLimitExceededError(
                http_resp=http_mock_response(error_response_body, 429)
            ),
            RateLimitExceededError(
                http_resp=http_mock_response(error_response_body, 429)
            ),
            RateLimitExceededError(
                http_resp=http_mock_response(error_response_body, 429)
            ),
            RateLimitExceededError(
                http_resp=http_mock_response(error_response_body, 429)
            ),
            RateLimitExceededError(
                http_resp=http_mock_response(error_response_body, 429)
            ),
            mock_response(response_body, 200),
        ]
        max_wait_in_sec = 1
        retry = openfga_sdk.configuration.RetryParams(
            max_retry=9, min_wait_in_ms=10, max_wait_in_sec=max_wait_in_sec
        )
        configuration = self.configuration
        configuration.store_id = store_id
        configuration.retry_params = retry

        async with openfga_sdk.ApiClient(configuration) as api_client:
            api_instance = open_fga_api.OpenFgaApi(api_client)
            body = CheckRequest(
                tuple_key=TupleKey(
                    object="document:2021-budget",
                    relation="reader",
                    user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                ),
            )
            api_response = await api_instance.check(
                body=body,
            )
            self.assertIsInstance(api_response, CheckResponse)
            self.assertTrue(api_response.allowed)
            mock_request.assert_called()
            self.assertEqual(mock_request.call_count, 9)
            self.assertEqual(mock_sleep.call_args[0][0], max_wait_in_sec)

    @patch("asyncio.sleep")
    @patch.object(rest.RESTClientObject, "request")
    async def test_429_error_retry_configured_unparseable_retry_after(
        self, mock_request, mock_sleep
    ):
        """
        Test to ensure 429 errors are handled properly.
        For this case, retry is configured and the Retry-After header is provided as an HTTP date.
        """
        response_body = '{"allowed": true, "resolution": "1234"}'
        error_response_body = """
            {
              "code": "rate_limit_exceeded",
              "message": "Rate Limit exceeded"
            }
        """
        retry_after_in_sec = 5
        five_seconds_from_now = f"{retry_after_in_sec}s"
        mock_http_response = http_mock_response(
            body=error_response_body,
            status=429,
            headers={"Retry-After": five_seconds_from_now},
        )
        mock_request.side_effect = [
            RateLimitExceededError(http_resp=mock_http_response),
            mock_response(response_body, 200),
        ]

        retry = openfga_sdk.configuration.RetryParams(
            max_retry=1, min_wait_in_ms=10, max_wait_in_sec=1
        )
        configuration = self.configuration
        configuration.store_id = store_id
        configuration.retry_params = retry
        async with openfga_sdk.ApiClient(configuration) as api_client:
            api_instance = open_fga_api.OpenFgaApi(api_client)
            body = CheckRequest(
                tuple_key=TupleKey(
                    object="document:2021-budget",
                    relation="reader",
                    user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                ),
            )
            api_response = await api_instance.check(
                body=body,
            )
            self.assertIsInstance(api_response, CheckResponse)
            self.assertTrue(api_response.allowed)
            mock_request.assert_called()
            self.assertEqual(mock_request.call_count, 2)
            self.assertNotEqual(mock_sleep.call_args[0][0], retry_after_in_sec)

    @patch("asyncio.sleep")
    @patch.object(rest.RESTClientObject, "request")
    async def test_429_error_retry_configured_with_http_date(
        self, mock_request, mock_sleep
    ):
        """
        Test to ensure 429 errors are handled properly.
        For this case, retry is configured and the Retry-After header is provided as an HTTP date.
        """
        response_body = '{"allowed": true, "resolution": "1234"}'
        error_response_body = """
            {
              "code": "rate_limit_exceeded",
              "message": "Rate Limit exceeded"
            }
        """
        retry_after_in_sec = 10
        ten_seconds_from_now = (
            datetime.now(timezone.utc) + timedelta(seconds=retry_after_in_sec)
        ).strftime("%a, %d %b %Y %H:%M:%S GMT")
        mock_http_response = http_mock_response(
            body=error_response_body,
            status=429,
            headers={"Retry-After": ten_seconds_from_now},
        )
        mock_request.side_effect = [
            RateLimitExceededError(http_resp=mock_http_response),
            mock_response(response_body, 200),
        ]

        retry = openfga_sdk.configuration.RetryParams(
            max_retry=1, min_wait_in_ms=10, max_wait_in_sec=15
        )
        configuration = self.configuration
        configuration.store_id = store_id
        configuration.retry_params = retry
        async with openfga_sdk.ApiClient(configuration) as api_client:
            api_instance = open_fga_api.OpenFgaApi(api_client)
            body = CheckRequest(
                tuple_key=TupleKey(
                    object="document:2021-budget",
                    relation="reader",
                    user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                ),
            )
            api_response = await api_instance.check(
                body=body,
            )
            self.assertIsInstance(api_response, CheckResponse)
            self.assertTrue(api_response.allowed)
            mock_request.assert_called()
            self.assertEqual(mock_request.call_count, 2)
            self.assertTrue(
                retry_after_in_sec - 2
                <= mock_sleep.call_args[0][0]
                <= retry_after_in_sec
            )

    @patch("asyncio.sleep")
    @patch.object(rest.RESTClientObject, "request")
    async def test_429_error_retry_configured_with_delay_seconds(
        self, mock_request, mock_sleep
    ):
        """
        Test to ensure 429 errors are handled properly.
        For this case, retry is configured and the Retry-After header is provided as an HTTP date.
        """
        response_body = '{"allowed": true, "resolution": "1234"}'
        error_response_body = """
            {
              "code": "rate_limit_exceeded",
              "message": "Rate Limit exceeded"
            }
        """
        retry_after_in_sec = 10
        mock_http_response = http_mock_response(
            body=error_response_body,
            status=429,
            headers={"Retry-After": retry_after_in_sec},
        )
        mock_request.side_effect = [
            RateLimitExceededError(http_resp=mock_http_response),
            mock_response(response_body, 200),
        ]

        retry = openfga_sdk.configuration.RetryParams(
            max_retry=1, min_wait_in_ms=10, max_wait_in_sec=1
        )
        configuration = self.configuration
        configuration.store_id = store_id
        configuration.retry_params = retry
        async with openfga_sdk.ApiClient(configuration) as api_client:
            api_instance = open_fga_api.OpenFgaApi(api_client)
            body = CheckRequest(
                tuple_key=TupleKey(
                    object="document:2021-budget",
                    relation="reader",
                    user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                ),
            )
            api_response = await api_instance.check(
                body=body,
            )
            self.assertIsInstance(api_response, CheckResponse)
            self.assertTrue(api_response.allowed)
            mock_request.assert_called()
            self.assertEqual(mock_request.call_count, 2)
            self.assertEqual(mock_sleep.call_args[0][0], retry_after_in_sec)

    @patch.object(rest.RESTClientObject, "request")
    async def test_500_error(self, mock_request):
        """
        Test to ensure 500 errors are handled properly
        """
        response_body = """
{
  "code": "internal_error",
  "message": "Internal Server Error"
}
        """
        mock_request.side_effect = ServiceException(
            http_resp=http_mock_response(response_body, 500)
        )

        configuration = self.configuration
        configuration.store_id = store_id
        configuration.retry_params.max_retry = 0

        async with openfga_sdk.ApiClient(configuration) as api_client:
            api_instance = open_fga_api.OpenFgaApi(api_client)
            body = CheckRequest(
                tuple_key=TupleKey(
                    object="document:2021-budget",
                    relation="reader",
                    user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                ),
            )
            with self.assertRaises(ServiceException) as api_exception:
                await api_instance.check(
                    body=body,
                )
            self.assertIsInstance(
                api_exception.exception.parsed_exception, InternalErrorMessageResponse
            )
            self.assertEqual(
                api_exception.exception.parsed_exception.code,
                InternalErrorCode.INTERNAL_ERROR,
            )
            self.assertEqual(
                api_exception.exception.parsed_exception.message,
                "Internal Server Error",
            )
            mock_request.assert_called()
            self.assertEqual(mock_request.call_count, 1)

    @patch.object(rest.RESTClientObject, "request")
    async def test_500_error_retry(self, mock_request):
        """
        Test to ensure 5xxx retries  are handled properly
        """
        response_body = """
{
  "code": "internal_error",
  "message": "Internal Server Error"
}
        """
        mock_request.side_effect = [
            ServiceException(http_resp=http_mock_response(response_body, 500)),
            ServiceException(http_resp=http_mock_response(response_body, 502)),
            ServiceException(http_resp=http_mock_response(response_body, 503)),
            ServiceException(http_resp=http_mock_response(response_body, 504)),
            mock_response(response_body, 200),
        ]

        retry = openfga_sdk.configuration.RetryParams(5, 10)
        configuration = self.configuration
        configuration.store_id = store_id
        configuration.retry_params = retry

        async with openfga_sdk.ApiClient(configuration) as api_client:
            api_instance = open_fga_api.OpenFgaApi(api_client)
            body = CheckRequest(
                tuple_key=TupleKey(
                    object="document:2021-budget",
                    relation="reader",
                    user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                ),
            )

            api_response = await api_instance.check(
                body=body,
            )

            self.assertIsInstance(api_response, CheckResponse)
            mock_request.assert_called()
            self.assertEqual(mock_request.call_count, 5)

    @patch.object(rest.RESTClientObject, "request")
    async def test_501_error_retry(self, mock_request):
        """
        Test to ensure 501 responses are not auto-retried
        """
        response_body = """
{
  "code": "not_implemented",
  "message": "Not Implemented"
}
        """
        mock_request.side_effect = [
            ServiceException(http_resp=http_mock_response(response_body, 501)),
            ServiceException(http_resp=http_mock_response(response_body, 501)),
            ServiceException(http_resp=http_mock_response(response_body, 501)),
            mock_response(response_body, 200),
        ]

        retry = openfga_sdk.configuration.RetryParams(5, 10)
        configuration = self.configuration
        configuration.store_id = store_id
        configuration.retry_params = retry

        async with openfga_sdk.ApiClient(configuration) as api_client:
            api_instance = open_fga_api.OpenFgaApi(api_client)
            body = CheckRequest(
                tuple_key=TupleKey(
                    object="document:2021-budget",
                    relation="reader",
                    user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                ),
            )
            with self.assertRaises(ServiceException):
                await api_instance.check(
                    body=body,
                )
            mock_request.assert_called()
            self.assertEqual(mock_request.call_count, 1)

    @patch.object(rest.RESTClientObject, "request")
    async def test_check_api_token(self, mock_request):
        """Test case for API token

        Check whether API token is send when configuration specifies credential method as api_token
        """

        # First, mock the response
        response_body = '{"allowed": true}'
        mock_request.return_value = mock_response(response_body, 200)

        configuration = self.configuration
        configuration.store_id = store_id
        configuration.credentials = Credentials(
            method="api_token",
            configuration=CredentialConfiguration(api_token="TOKEN1"),
        )
        async with openfga_sdk.ApiClient(configuration) as api_client:
            api_instance = open_fga_api.OpenFgaApi(api_client)
            body = CheckRequest(
                tuple_key=TupleKey(
                    object="document:2021-budget",
                    relation="reader",
                    user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                ),
            )
            api_response = await api_instance.check(
                body=body,
            )
            self.assertIsInstance(api_response, CheckResponse)
            self.assertTrue(api_response.allowed)
            # Make sure the API was called with the right data
            expected_headers = urllib3.response.HTTPHeaderDict(
                {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "User-Agent": USER_AGENT,
                    "Authorization": "Bearer TOKEN1",
                }
            )
            mock_request.assert_called_once_with(
                "POST",
                "http://api.fga.example/stores/01H0H015178Y2V4CX10C2KGHF4/check",
                headers=expected_headers,
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
    async def test_check_custom_header(self, mock_request):
        """Test case for custom header

        Check whether custom header can be added
        """

        # First, mock the response
        response_body = '{"allowed": true}'
        mock_request.return_value = mock_response(response_body, 200)

        configuration = self.configuration
        configuration.store_id = store_id
        async with openfga_sdk.ApiClient(configuration) as api_client:
            api_client.set_default_header("Custom Header", "custom value")
            api_instance = open_fga_api.OpenFgaApi(api_client)
            body = CheckRequest(
                tuple_key=TupleKey(
                    object="document:2021-budget",
                    relation="reader",
                    user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                ),
            )
            api_response = await api_instance.check(
                body=body,
            )
            self.assertIsInstance(api_response, CheckResponse)
            self.assertTrue(api_response.allowed)
            # Make sure the API was called with the right data
            expected_headers = urllib3.response.HTTPHeaderDict(
                {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "User-Agent": USER_AGENT,
                    "Custom Header": "custom value",
                }
            )
            mock_request.assert_called_once_with(
                "POST",
                "http://api.fga.example/stores/01H0H015178Y2V4CX10C2KGHF4/check",
                headers=expected_headers,
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
    async def test_list_stores_with_name(self, mock_request):
        """Test case for list_stores with name parameter

        Get stores filtered by name
        """
        response_body = """
{
  "stores": [
    {
      "id": "01YCP46JKYM8FJCQ37NMBYHE5X",
      "name": "test-store",
      "created_at": "2022-07-25T21:15:37.524Z",
      "updated_at": "2022-07-25T21:15:37.524Z",
      "deleted_at": "2022-07-25T21:15:37.524Z"
    },
    {
      "id": "01YCP46JKYM8FJCQ37NMBYHE6X",
      "name": "other-store",
      "created_at": "2022-07-25T21:15:37.524Z",
      "updated_at": "2022-07-25T21:15:37.524Z",
      "deleted_at": "2022-07-25T21:15:37.524Z"
    }
  ],
  "continuation_token": "token123"
}
            """
        mock_request.return_value = mock_response(response_body, 200)
        configuration = self.configuration
        async with openfga_sdk.ApiClient(configuration) as api_client:
            api_instance = open_fga_api.OpenFgaApi(api_client)
            # Get stores filtered by name
            api_response = await api_instance.list_stores(name="test-store")
            self.assertIsInstance(api_response, ListStoresResponse)
            self.assertEqual(api_response.continuation_token, "token123")
            store1 = Store(
                id="01YCP46JKYM8FJCQ37NMBYHE5X",
                name="test-store",
                created_at=datetime.fromisoformat("2022-07-25T21:15:37.524+00:00"),
                updated_at=datetime.fromisoformat("2022-07-25T21:15:37.524+00:00"),
                deleted_at=datetime.fromisoformat("2022-07-25T21:15:37.524+00:00"),
            )
            store2 = Store(
                id="01YCP46JKYM8FJCQ37NMBYHE6X",
                name="other-store",
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
                query_params=[("name", "test-store")],
                post_params=[],
                _preload_content=ANY,
                _request_timeout=None,
            )
            await api_client.close()

    @patch.object(rest.RESTClientObject, "request")
    async def test_read_with_tuple_key_user(self, mock_request):
        """Test case for read with tuple key containing user

        Get tuples from the store that matches a query with user
        """
        response_body = """
            {
  "tuples": [
    {
      "key": {
        "user": "user:bob",
        "relation": "reader",
        "object": "document:2021-budget"
      },
      "timestamp": "2021-10-06T15:32:11.128Z"
    }
  ],
  "continuation_token": "token123"
}
        """
        mock_request.return_value = mock_response(response_body, 200)
        configuration = self.configuration
        configuration.store_id = store_id
        async with openfga_sdk.ApiClient(configuration) as api_client:
            api_instance = open_fga_api.OpenFgaApi(api_client)
            body = ReadRequest(
                tuple_key=ReadRequestTupleKey(
                    object="document:2021-budget",
                    relation="reader",
                    user="user:bob",
                ),
            )
            api_response = await api_instance.read(body=body)
            self.assertIsInstance(api_response, ReadResponse)
            key = TupleKey(
                user="user:bob",
                relation="reader",
                object="document:2021-budget",
            )
            timestamp = datetime.fromisoformat("2021-10-06T15:32:11.128+00:00")
            expected_data = ReadResponse(
                tuples=[Tuple(key=key, timestamp=timestamp)],
                continuation_token="token123",
            )
            self.assertEqual(api_response, expected_data)
            mock_request.assert_called_once_with(
                "POST",
                "http://api.fga.example/stores/01H0H015178Y2V4CX10C2KGHF4/read",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "tuple_key": {
                        "object": "document:2021-budget",
                        "relation": "reader",
                        "user": "user:bob",
                    }
                },
                _preload_content=ANY,
                _request_timeout=None,
            )
            await api_client.close()

    @patch.object(rest.RESTClientObject, "request")
    async def test_read_with_type_only_object(self, mock_request):
        """Test case for read with type-only object

        Get tuples from the store that matches a query with type-only object
        """
        response_body = """
            {
  "tuples": [
    {
      "key": {
        "user": "user:bob",
        "relation": "reader",
        "object": "document:2021-budget"
      },
      "timestamp": "2021-10-06T15:32:11.128Z"
    }
  ],
  "continuation_token": "token123"
}
        """
        mock_request.return_value = mock_response(response_body, 200)
        configuration = self.configuration
        configuration.store_id = store_id
        async with openfga_sdk.ApiClient(configuration) as api_client:
            api_instance = open_fga_api.OpenFgaApi(api_client)
            body = ReadRequest(
                tuple_key=ReadRequestTupleKey(
                    object="document:",
                    relation="reader",
                    user="user:bob",
                ),
            )
            api_response = await api_instance.read(body=body)
            self.assertIsInstance(api_response, ReadResponse)
            key = TupleKey(
                user="user:bob",
                relation="reader",
                object="document:2021-budget",
            )
            timestamp = datetime.fromisoformat("2021-10-06T15:32:11.128+00:00")
            expected_data = ReadResponse(
                tuples=[Tuple(key=key, timestamp=timestamp)],
                continuation_token="token123",
            )
            self.assertEqual(api_response, expected_data)
            mock_request.assert_called_once_with(
                "POST",
                "http://api.fga.example/stores/01H0H015178Y2V4CX10C2KGHF4/read",
                headers=ANY,
                query_params=[],
                post_params=[],
                body={
                    "tuple_key": {
                        "object": "document:",
                        "relation": "reader",
                        "user": "user:bob",
                    }
                },
                _preload_content=ANY,
                _request_timeout=None,
            )
            await api_client.close()

    @patch.object(rest.RESTClientObject, "request")
    async def test_check_custom_header_override_default_header(self, mock_request):
        """Test case for per-request custom header overriding default header

        Per-request custom headers should override default headers with the same name
        """

        # First, mock the response
        response_body = '{"allowed": true}'
        mock_request.return_value = mock_response(response_body, 200)

        configuration = self.configuration
        configuration.store_id = store_id
        async with openfga_sdk.ApiClient(configuration) as api_client:
            # Set a default header
            api_client.set_default_header("X-Custom-Header", "default-value")
            api_instance = open_fga_api.OpenFgaApi(api_client)
            body = CheckRequest(
                tuple_key=TupleKey(
                    object="document:2021-budget",
                    relation="reader",
                    user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                ),
            )
            # Make request with per-request custom header that should override the default
            api_response = await api_instance.check(
                body=body,
                _headers={"X-Custom-Header": "per-request-value"},
            )
            self.assertIsInstance(api_response, CheckResponse)
            self.assertTrue(api_response.allowed)
            # Make sure the API was called with the per-request header value, not the default
            expected_headers = urllib3.response.HTTPHeaderDict(
                {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "User-Agent": USER_AGENT,
                    "X-Custom-Header": "per-request-value",  # Should be the per-request value
                }
            )
            mock_request.assert_called_once_with(
                "POST",
                "http://api.fga.example/stores/01H0H015178Y2V4CX10C2KGHF4/check",
                headers=expected_headers,
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
    async def test_check_per_request_header_and_default_header_coexist(
        self, mock_request
    ):
        """Test case for per-request custom header and default header coexisting

        Per-request custom headers should be merged with default headers
        """

        # First, mock the response
        response_body = '{"allowed": true}'
        mock_request.return_value = mock_response(response_body, 200)

        configuration = self.configuration
        configuration.store_id = store_id
        async with openfga_sdk.ApiClient(configuration) as api_client:
            # Set a default header
            api_client.set_default_header("X-Default-Header", "default-value")
            api_instance = open_fga_api.OpenFgaApi(api_client)
            body = CheckRequest(
                tuple_key=TupleKey(
                    object="document:2021-budget",
                    relation="reader",
                    user="user:81684243-9356-4421-8fbf-a4f8d36aa31b",
                ),
            )
            # Make request with per-request custom header (different from default)
            api_response = await api_instance.check(
                body=body,
                _headers={"X-Per-Request-Header": "per-request-value"},
            )
            self.assertIsInstance(api_response, CheckResponse)
            self.assertTrue(api_response.allowed)
            # Make sure both headers are present in the request
            expected_headers = urllib3.response.HTTPHeaderDict(
                {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "User-Agent": USER_AGENT,
                    "X-Default-Header": "default-value",  # Default header preserved
                    "X-Per-Request-Header": "per-request-value",  # Per-request header added
                }
            )
            mock_request.assert_called_once_with(
                "POST",
                "http://api.fga.example/stores/01H0H015178Y2V4CX10C2KGHF4/check",
                headers=expected_headers,
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


if __name__ == "__main__":
    unittest.main()
