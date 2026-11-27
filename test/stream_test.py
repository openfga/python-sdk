import aiohttp
import pytest
import urllib3

from openfga_sdk import OpenFgaClient as AsyncOpenFgaClient
from openfga_sdk.api_client import ApiClient as AsyncApiClient
from openfga_sdk.client import ClientConfiguration
from openfga_sdk.client.models import ClientListObjectsRequest
from openfga_sdk.configuration import Configuration, RetryParams
from openfga_sdk.sync import OpenFgaClient as SyncOpenFgaClient
from openfga_sdk.sync.api_client import ApiClient as SyncApiClient


CALL_ARGS = {
    "response_types_map": {},
    "_return_http_data_only": True,
    "_streaming": True,
}
STORE_ID = "01YCP46JKYM8FJCQ37NMBYHE5X"
LIST_OBJECTS = ClientListObjectsRequest(
    user="user:anne", relation="viewer", type="document"
)
STREAMED_LIST_OBJECTS = {
    "operation_name": "StreamedListObjects",
    "method": "POST",
    "path": "/stores/{store_id}/streamed-list-objects",
    "path_params": {"store_id": STORE_ID},
    "body": {},
}


def make_configuration(url):
    return Configuration(api_url=url, retry_params=RetryParams(max_retry=1))


def make_client_configuration(url):
    return ClientConfiguration(
        api_url=url, store_id=STORE_ID, retry_params=RetryParams(max_retry=0)
    )


@pytest.mark.parametrize("failure", ["drop", "503"])
@pytest.mark.asyncio
async def test_async_stream_retries_until_connected(server, sleeps, failure):
    server.actions.append(failure)
    async with AsyncApiClient(make_configuration(server.url)) as client:
        stream = await client.call_api("/stream", "POST", **CALL_ARGS)
        received = [obj async for obj in stream]

    assert received == server.objects
    assert server.requests == ["POST", "POST"]


@pytest.mark.parametrize("failure", ["drop", "503"])
def test_sync_stream_retries_until_connected(server, sleeps, failure):
    server.actions.append(failure)
    with SyncApiClient(make_configuration(server.url)) as client:
        received = list(client.call_api("/stream", "POST", **CALL_ARGS))

    assert received == server.objects
    assert server.requests == ["POST", "POST"]


# Once the body has started, a failure raises to the caller instead of
# restarting the stream, which would repeat the objects already yielded.
@pytest.mark.asyncio
async def test_async_stream_raises_without_retry_once_connected(server, sleeps):
    server.actions.append("truncate")
    received = []
    async with AsyncApiClient(make_configuration(server.url)) as client:
        stream = await client.call_api("/stream", "POST", **CALL_ARGS)
        with pytest.raises(aiohttp.ClientPayloadError):
            async for obj in stream:
                received.append(obj)

    assert received == server.objects[:1]
    assert server.requests == ["POST"]
    assert sleeps == []


def test_sync_stream_raises_without_retry_once_connected(server, sleeps):
    server.actions.append("truncate")
    received = []
    with SyncApiClient(make_configuration(server.url)) as client:
        stream = client.call_api("/stream", "POST", **CALL_ARGS)
        with pytest.raises(urllib3.exceptions.ProtocolError):
            received.extend(stream)

    assert received == server.objects[:1]
    assert server.requests == ["POST"]
    assert sleeps == []


# Closing a public stream early must hand the response back right away, not
# when the client closes. The wrappers' own tests check the close is forwarded
# at each layer; these check the end result with the real transports.
@pytest.mark.asyncio
async def test_async_closing_streamed_list_objects_releases_response(server, releases):
    async with AsyncOpenFgaClient(make_client_configuration(server.url)) as client:
        stream = client.streamed_list_objects(LIST_OBJECTS)
        first = await anext(stream)
        await stream.aclose()

        assert first.object == "document:0"
        assert releases == [1]


@pytest.mark.asyncio
async def test_async_closing_streamed_api_request_releases_response(server, releases):
    async with AsyncOpenFgaClient(make_client_configuration(server.url)) as client:
        stream = client.execute_streamed_api_request(**STREAMED_LIST_OBJECTS)
        first = await anext(stream)
        await stream.aclose()

        assert first == server.objects[0]
        assert releases == [1]


def test_sync_closing_streamed_list_objects_releases_response(server, releases):
    with SyncOpenFgaClient(make_client_configuration(server.url)) as client:
        stream = client.streamed_list_objects(LIST_OBJECTS)
        first = next(stream)
        stream.close()

        assert first.object == "document:0"
        assert releases[0] >= 1


def test_sync_closing_streamed_api_request_releases_response(server, releases):
    with SyncOpenFgaClient(make_client_configuration(server.url)) as client:
        stream = client.execute_streamed_api_request(**STREAMED_LIST_OBJECTS)
        first = next(stream)
        stream.close()

        assert first == server.objects[0]
        assert releases[0] >= 1
