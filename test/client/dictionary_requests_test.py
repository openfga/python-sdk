"""Dictionary requests must reach the wire in the same shape as SDK models."""

import copy
import inspect
import json

from unittest.mock import AsyncMock, Mock, patch

import pytest
import pytest_asyncio
import urllib3

from openfga_sdk.client import ClientConfiguration, OpenFgaClient
from openfga_sdk.client.models.check_request import ClientCheckRequest
from openfga_sdk.client.models.tuple import ClientTuple
from openfga_sdk.client.models.write_transaction_opts import WriteTransactionOpts
from openfga_sdk.rest import RESTResponse
from openfga_sdk.sync import OpenFgaClient as SyncOpenFgaClient


STORE_ID = "01YCP46JKYM8FJCQ37NMBYHE5X"
MODEL_ID = "01GXSA8YR785C4FYS3C0RTG7B1"
TUPLE = {"user": "user:bob", "relation": "viewer", "object": "document:roadmap"}
CONDITION = {"name": "valid_grant", "context": {"expires_at": "2026-12-01T00:00:00Z"}}
CONDITIONAL_TUPLE = {**TUPLE, "condition": CONDITION}
CONTEXT = {"current_time": "2026-11-01T00:00:00Z", "attributes": {"verified": True}}
CHECK = {**TUPLE, "contextual_tuples": [CONDITIONAL_TUPLE], "context": CONTEXT}
CHECK_PAYLOAD = {
    "tuple_key": TUPLE,
    "contextual_tuples": {"tuple_keys": [CONDITIONAL_TUPLE]},
    "context": CONTEXT,
    "authorization_model_id": MODEL_ID,
}
LIST_OBJECTS = {
    "user": "user:bob",
    "relation": "viewer",
    "type": "document",
    "contextual_tuples": [CONDITIONAL_TUPLE],
    "context": CONTEXT,
}
LIST_OBJECTS_PAYLOAD = {
    **LIST_OBJECTS,
    "contextual_tuples": {"tuple_keys": [CONDITIONAL_TUPLE]},
    "authorization_model_id": MODEL_ID,
}

# Each expected payload describes the public API contract, not parser internals.
CASES = [
    (
        "create_store",
        {"name": "dictionary store"},
        {"id": STORE_ID, "name": "dictionary store"},
        {"name": "dictionary store"},
    ),
    (
        "write_authorization_model",
        {"schema_version": "1.1", "type_definitions": [{"type": "user"}]},
        {"authorization_model_id": MODEL_ID},
        {"schema_version": "1.1", "type_definitions": [{"type": "user"}]},
    ),
    ("read", TUPLE, {"tuples": [], "continuation_token": ""}, {"tuple_key": TUPLE}),
    ("read", {}, {"tuples": [], "continuation_token": ""}, {}),
    ("read", None, {"tuples": [], "continuation_token": ""}, {}),
    (
        "read_changes",
        {"type": "document", "start_time": "2026-01-01T00:00:00Z"},
        {"changes": [], "continuation_token": ""},
        None,
    ),
    ("check", CHECK, {"allowed": True}, CHECK_PAYLOAD),
    ("client_batch_check", [CHECK], {"allowed": True}, CHECK_PAYLOAD),
    (
        "batch_check",
        {"checks": [{**CHECK, "correlation_id": "first"}]},
        {"result": {"first": {"allowed": True}}},
        {
            "checks": [
                {
                    "tuple_key": TUPLE,
                    "contextual_tuples": {"tuple_keys": [CONDITIONAL_TUPLE]},
                    "context": CONTEXT,
                    "correlation_id": "first",
                }
            ],
            "authorization_model_id": MODEL_ID,
        },
    ),
    (
        "write",
        {"writes": [CONDITIONAL_TUPLE], "deletes": [TUPLE]},
        {},
        {
            "writes": {"tuple_keys": [CONDITIONAL_TUPLE], "on_duplicate": "error"},
            "deletes": {"tuple_keys": [TUPLE], "on_missing": "error"},
            "authorization_model_id": MODEL_ID,
        },
    ),
    (
        "write_tuples",
        [CONDITIONAL_TUPLE],
        {},
        {
            "writes": {"tuple_keys": [CONDITIONAL_TUPLE], "on_duplicate": "error"},
            "authorization_model_id": MODEL_ID,
        },
    ),
    (
        "delete_tuples",
        [TUPLE],
        {},
        {
            "deletes": {"tuple_keys": [TUPLE], "on_missing": "error"},
            "authorization_model_id": MODEL_ID,
        },
    ),
    (
        "expand",
        {
            "relation": "viewer",
            "object": "document:roadmap",
            "contextual_tuples": [CONDITIONAL_TUPLE],
        },
        {"tree": {"root": {"name": "document:roadmap#viewer"}}},
        {
            "tuple_key": {"relation": "viewer", "object": "document:roadmap"},
            "contextual_tuples": {"tuple_keys": [CONDITIONAL_TUPLE]},
            "authorization_model_id": MODEL_ID,
        },
    ),
    ("list_objects", LIST_OBJECTS, {"objects": []}, LIST_OBJECTS_PAYLOAD),
    (
        "list_relations",
        {
            "user": "user:bob",
            "relations": ["viewer"],
            "object": "document:roadmap",
            "contextual_tuples": [CONDITIONAL_TUPLE],
            "context": CONTEXT,
        },
        {"allowed": True},
        CHECK_PAYLOAD,
    ),
    (
        "list_users",
        {
            "object": {"type": "document", "id": "roadmap"},
            "relation": "viewer",
            "user_filters": [{"type": "user"}],
            "contextual_tuples": [CONDITIONAL_TUPLE],
            "context": CONTEXT,
        },
        {"users": []},
        {
            "object": {"type": "document", "id": "roadmap"},
            "relation": "viewer",
            "user_filters": [{"type": "user"}],
            "contextual_tuples": [CONDITIONAL_TUPLE],
            "context": CONTEXT,
            "authorization_model_id": MODEL_ID,
        },
    ),
    (
        "write_assertions",
        [{**TUPLE, "expectation": True}],
        {},
        {"assertions": [{"tuple_key": TUPLE, "expectation": True}]},
    ),
]


@pytest_asyncio.fixture(params=["async", "sync"])
async def client(request):
    configuration = ClientConfiguration(
        api_url="http://api.fga.example",
        store_id=STORE_ID,
        authorization_model_id=MODEL_ID,
    )
    cls = OpenFgaClient if request.param == "async" else SyncOpenFgaClient
    return cls(configuration)


async def invoke(client, method, body, options=None):
    result = getattr(client, method)(body, options)
    return await result if inspect.isawaitable(result) else result


async def close(client):
    result = client.close()
    if inspect.isawaitable(result):
        await result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method,body,response,expected", CASES, ids=[case[0] for case in CASES]
)
async def test_dictionary_request_serialization(
    client, method, body, response, expected
):
    body = copy.deepcopy(body)
    original = copy.deepcopy(body)
    data = json.dumps(response).encode()
    http_response = urllib3.HTTPResponse(
        data,
        status=200,
        headers={"content-type": "application/json"},
    )
    response = RESTResponse(http_response, data)
    mock_cls = AsyncMock if isinstance(client, OpenFgaClient) else Mock
    with patch.object(
        client._api_client.rest_client, "request", new_callable=mock_cls
    ) as request:
        request.return_value = response
        try:
            await invoke(client, method, body)
            request.assert_called_once()
            assert request.call_args.kwargs["body"] == expected
            if method == "read_changes":
                assert dict(request.call_args.kwargs["query_params"]) == original
            assert body == original
        finally:
            await close(client)


@pytest.mark.asyncio
async def test_streamed_dictionary_request(client):
    body = copy.deepcopy(LIST_OBJECTS)

    async def async_responses():
        yield {"result": {"object": "document:roadmap"}}

    mock_cls = AsyncMock if isinstance(client, OpenFgaClient) else Mock
    with patch.object(
        client._api, "streamed_list_objects", new_callable=mock_cls
    ) as request:
        request.return_value = (
            async_responses()
            if isinstance(client, OpenFgaClient)
            else iter([{"result": {"object": "document:roadmap"}}])
        )
        try:
            stream = client.streamed_list_objects(body)
            results = (
                [item async for item in stream]
                if isinstance(client, OpenFgaClient)
                else list(stream)
            )
            assert [item.object for item in results] == ["document:roadmap"]
            payload = client._api_client.sanitize_for_serialization(
                request.call_args.kwargs["body"]
            )
            assert payload == LIST_OBJECTS_PAYLOAD
            assert body == LIST_OBJECTS
        finally:
            await close(client)


@pytest.mark.asyncio
async def test_batch_check_does_not_insert_correlation_id_in_dictionary(client):
    body = {"checks": [copy.deepcopy(CHECK)]}
    original = copy.deepcopy(body)
    mock_cls = AsyncMock if isinstance(client, OpenFgaClient) else Mock
    with patch.object(client._api, "batch_check", new_callable=mock_cls) as request:
        request.return_value = Mock(result={})
        try:
            await invoke(client, "batch_check", body)
            sent_check = request.call_args.args[0].checks[0]
            assert sent_check.correlation_id
            assert body == original
        finally:
            await close(client)


@pytest.mark.asyncio
async def test_dictionary_can_contain_existing_tuple_models(client):
    contextual_tuple = ClientTuple(**TUPLE)
    body = {**TUPLE, "contextual_tuples": [contextual_tuple, copy.deepcopy(TUPLE)]}
    mock_cls = AsyncMock if isinstance(client, OpenFgaClient) else Mock
    with patch.object(client._api, "check", new_callable=mock_cls) as request:
        try:
            await invoke(client, "check", body)
            payload = client._api_client.sanitize_for_serialization(
                request.call_args.kwargs["body"]
            )
            assert payload["contextual_tuples"]["tuple_keys"] == [TUPLE, TUPLE]
            assert body["contextual_tuples"][0] is contextual_tuple
        finally:
            await close(client)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "body",
    [
        {"relation": "viewer"},
        {**TUPLE, "unexpected": True},
        {**TUPLE, "contextual_tuples": [{"user": "user:bob"}]},
    ],
)
async def test_invalid_dictionary_is_rejected_before_http_request(client, body):
    mock_cls = AsyncMock if isinstance(client, OpenFgaClient) else Mock
    with patch.object(client._api, "check", new_callable=mock_cls) as request:
        try:
            with pytest.raises(TypeError):
                await invoke(client, "check", body)
            request.assert_not_called()
        finally:
            await close(client)


def test_existing_request_models_are_preserved():
    from openfga_sdk.client.request import parse_request

    request = ClientCheckRequest(**TUPLE)
    assert parse_request(request, ClientCheckRequest) is request


@pytest.mark.asyncio
async def test_dictionary_write_without_transaction(client):
    body = {"writes": [copy.deepcopy(CONDITIONAL_TUPLE), copy.deepcopy(TUPLE)]}
    original = copy.deepcopy(body)
    mock_cls = AsyncMock if isinstance(client, OpenFgaClient) else Mock
    with patch.object(client._api, "write", new_callable=mock_cls) as request:
        try:
            result = await invoke(
                client,
                "write",
                body,
                {"transaction": WriteTransactionOpts(disabled=True, max_per_chunk=1)},
            )
            assert request.call_count == 2
            payloads = [
                client._api_client.sanitize_for_serialization(call.args[0])
                for call in request.call_args_list
            ]
            assert [payload["writes"]["tuple_keys"] for payload in payloads] == [
                [CONDITIONAL_TUPLE],
                [TUPLE],
            ]
            assert all(item.success for item in result.writes)
            assert body == original
        finally:
            await close(client)


@pytest.mark.asyncio
async def test_dictionary_batch_check_across_chunks(client):
    body = {
        "checks": [
            {**TUPLE, "correlation_id": "first"},
            {**TUPLE, "correlation_id": "second"},
        ]
    }
    original = copy.deepcopy(body)
    mock_cls = AsyncMock if isinstance(client, OpenFgaClient) else Mock
    with patch.object(client._api, "batch_check", new_callable=mock_cls) as request:
        request.return_value = Mock(result={})
        try:
            await invoke(client, "batch_check", body, {"max_batch_size": 1})
            assert request.call_count == 2
            assert {
                call.args[0].checks[0].correlation_id for call in request.call_args_list
            } == {"first", "second"}
            assert body == original
        finally:
            await close(client)
