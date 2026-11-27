import asyncio
import json
import socket
import ssl
import time

from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Event, Thread
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest
import urllib3

from openfga_sdk import OpenFgaClient as AsyncOpenFgaClient
from openfga_sdk.api_client import ApiClient as AsyncApiClient
from openfga_sdk.client import ClientConfiguration
from openfga_sdk.client.models import ClientListObjectsRequest
from openfga_sdk.configuration import Configuration, RetryParams
from openfga_sdk.credentials import CredentialConfiguration, Credentials
from openfga_sdk.exceptions import ServiceException
from openfga_sdk.rest import RESTClientObject as AsyncRESTClientObject
from openfga_sdk.sync import OpenFgaClient as SyncOpenFgaClient
from openfga_sdk.sync.api_client import ApiClient as SyncApiClient
from openfga_sdk.sync.open_fga_api import OpenFgaApi as SyncOpenFgaApi
from openfga_sdk.telemetry.attributes import TelemetryAttributes
from openfga_sdk.telemetry.metrics import TelemetryMetrics


CALL_ARGS = {"response_types_map": {}, "_return_http_data_only": True}
OBJECTS = [{"result": {"object": f"document:{i}"}} for i in range(3)]
NDJSON = b"".join(json.dumps(obj).encode() + b"\n" for obj in OBJECTS)
RETRY_AFTER_IN_SEC = 7
STORE_ID = "01YCP46JKYM8FJCQ37NMBYHE5X"
LIST_OBJECTS = ClientListObjectsRequest(
    user="user:anne", relation="viewer", type="document"
)
# aiohttp 3.10 replays idempotent requests with no way to turn it off.
aiohttp_replay_is_configurable = pytest.mark.skipif(
    aiohttp.__version__.startswith("3.10."),
    reason="aiohttp 3.10 has no switch for its connection replay",
)
# The first retry waits random_time(0, min_wait_in_ms) seconds.
MIN_WAIT_IN_SEC = RetryParams().min_wait_in_ms / 1000

# The configured max_retry=1 allows two attempts; the per-call override allows one.
exhausted_cases = pytest.mark.parametrize(
    "retry_params,attempts",
    [
        pytest.param(None, 2, id="retries-exhausted"),
        pytest.param(RetryParams(max_retry=0), 1, id="retries-disabled-per-call"),
    ],
)


def make_configuration(url, **kwargs):
    return Configuration(api_url=url, retry_params=RetryParams(max_retry=1), **kwargs)


def make_client_configuration(url):
    return ClientConfiguration(
        api_url=url, store_id=STORE_ID, retry_params=RetryParams(max_retry=0)
    )


@dataclass
class FakeServer:
    url: str
    actions: list[str] = field(default_factory=list)
    requests: list[str] = field(default_factory=list)


@pytest.fixture
def server():
    """
    Replies to each request with the next queued action, then with 200:
    "drop" closes the connection without a response, "hang" never responds,
    "503" sends a 503 with a Retry-After header and "truncate" closes the
    connection after the first chunk of the body.
    """
    stopping = Event()

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, format, *args):
            pass

        def _respond(self):
            self.rfile.read(int(self.headers.get("Content-Length", 0)))
            fake.requests.append(self.command)
            action = fake.actions.pop(0) if fake.actions else "200"
            if action == "hang":
                stopping.wait(5)
                action = "drop"
            if action == "drop":
                self.close_connection = True
                return

            self.send_response(503 if action == "503" else 200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Transfer-Encoding", "chunked")
            if action == "503":
                self.send_header("Retry-After", str(RETRY_AFTER_IN_SEC))
            self.end_headers()
            for line in (b"{}" if action == "503" else NDJSON).splitlines(True):
                self.wfile.write(b"%x\r\n%s\r\n" % (len(line), line))
                if action == "truncate":
                    self.close_connection = True
                    return
            self.wfile.write(b"0\r\n\r\n")

        do_GET = do_POST = _respond

    with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as httpd:
        fake = FakeServer(url=f"http://127.0.0.1:{httpd.server_port}")
        thread = Thread(
            target=httpd.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True
        )
        thread.start()
        try:
            yield fake
        finally:
            stopping.set()
            httpd.shutdown()
            thread.join()


@pytest.fixture
def sleeps(monkeypatch):
    """Skips time.sleep and asyncio.sleep; the list records the requested waits."""
    waits = []

    async def async_sleep(seconds):
        waits.append(seconds)

    monkeypatch.setattr(time, "sleep", waits.append)
    monkeypatch.setattr(asyncio, "sleep", async_sleep)
    return waits


@pytest.fixture
def releases(monkeypatch):
    """Counts the HTTP responses handed back to the aiohttp or urllib3 pool."""
    count = [0]
    release = aiohttp.ClientResponse.release
    release_conn = urllib3.response.HTTPResponse.release_conn

    def counting_release(self):
        count[0] += 1
        return release(self)

    def counting_release_conn(self):
        count[0] += 1
        return release_conn(self)

    monkeypatch.setattr(aiohttp.ClientResponse, "release", counting_release)
    monkeypatch.setattr(
        urllib3.response.HTTPResponse, "release_conn", counting_release_conn
    )
    return count


@pytest.fixture
def resend_counts(monkeypatch):
    """The http.request.resend_count of every request metric recorded."""
    counts = []

    def request(self, attributes, configuration=None):
        counts.append(attributes[TelemetryAttributes.http_request_resend_count])

    monkeypatch.setattr(TelemetryMetrics, "request", request)
    return counts


@pytest.mark.asyncio
async def test_async_retries_dropped_connection(server, sleeps, resend_counts):
    server.actions.append("drop")
    async with AsyncApiClient(make_configuration(server.url)) as client:
        await client.call_api("/check", "POST", **CALL_ARGS)

    assert server.requests == ["POST", "POST"]
    assert resend_counts == [0, 1]
    assert len(sleeps) == 1
    assert MIN_WAIT_IN_SEC <= sleeps[0] < 2 * MIN_WAIT_IN_SEC


def test_sync_retries_dropped_connection(server, sleeps, resend_counts):
    server.actions.append("drop")
    with SyncApiClient(make_configuration(server.url)) as client:
        client.call_api("/check", "POST", **CALL_ARGS)

    assert server.requests == ["POST", "POST"]
    assert resend_counts == [0, 1]
    assert len(sleeps) == 1
    assert MIN_WAIT_IN_SEC <= sleeps[0] < 2 * MIN_WAIT_IN_SEC


@pytest.mark.asyncio
async def test_async_retries_timeout(server, sleeps, resend_counts):
    server.actions.append("hang")
    configuration = make_configuration(server.url, timeout_millisec=200)
    async with AsyncApiClient(configuration) as client:
        await client.call_api("/check", "POST", **CALL_ARGS)

    assert server.requests == ["POST", "POST"]
    assert resend_counts == [0, 1]


def test_sync_retries_timeout(server, sleeps, resend_counts):
    server.actions.append("hang")
    configuration = make_configuration(server.url, timeout_millisec=200)
    with SyncApiClient(configuration) as client:
        client.call_api("/check", "POST", **CALL_ARGS)

    assert server.requests == ["POST", "POST"]
    assert resend_counts == [0, 1]


# Every attempt is recorded, including the last failed one.
@pytest.mark.parametrize(
    "failure,error",
    [
        pytest.param("drop", aiohttp.ServerDisconnectedError, id="network"),
        pytest.param("503", ServiceException, id="status"),
    ],
)
@exhausted_cases
@pytest.mark.asyncio
async def test_async_raises_when_out_of_retries(
    server, sleeps, resend_counts, failure, error, retry_params, attempts
):
    server.actions.extend([failure] * attempts)
    async with AsyncApiClient(make_configuration(server.url)) as client:
        with pytest.raises(error):
            await client.call_api(
                "/check", "POST", _retry_params=retry_params, **CALL_ARGS
            )

    assert server.requests == ["POST"] * attempts
    assert resend_counts == list(range(attempts))


# urllib3 would otherwise resend the GET on its own.
@pytest.mark.parametrize(
    "failure,error",
    [
        pytest.param("drop", urllib3.exceptions.ProtocolError, id="network"),
        pytest.param("503", ServiceException, id="status"),
    ],
)
@exhausted_cases
def test_sync_raises_when_out_of_retries(
    server, sleeps, resend_counts, failure, error, retry_params, attempts
):
    server.actions.extend([failure] * attempts)
    with SyncApiClient(make_configuration(server.url)) as client:
        with pytest.raises(error):
            client.call_api("/stores", "GET", _retry_params=retry_params, **CALL_ARGS)

    assert server.requests == ["GET"] * attempts
    assert resend_counts == list(range(attempts))


# With its default Retry, urllib3 would retry a GET that got a 503 with a
# Retry-After header itself, sleeping for the uncapped header value each time.
def test_sync_only_sdk_handles_retry_after(server, sleeps, monkeypatch):
    urllib3_sleep = MagicMock()
    monkeypatch.setattr(urllib3.Retry, "sleep", urllib3_sleep)
    server.actions.append("503")
    with SyncApiClient(make_configuration(server.url)) as client:
        client.call_api("/stores", "GET", **CALL_ARGS)

    assert server.requests == ["GET", "GET"]
    assert sleeps == [RETRY_AFTER_IN_SEC]
    urllib3_sleep.assert_not_called()


def test_sync_retries_unreachable_proxy(sleeps):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]

    configuration = make_configuration("http://fga.example")
    configuration.proxy = f"http://127.0.0.1:{port}"
    with SyncApiClient(configuration) as client:
        with pytest.raises(urllib3.exceptions.ProxyError):
            client.call_api("/check", "POST", **CALL_ARGS)

    assert len(sleeps) == 1


@pytest.mark.parametrize(
    "error",
    [
        pytest.param(
            aiohttp.ClientConnectorCertificateError(
                MagicMock(), ssl.SSLCertVerificationError("certificate verify failed")
            ),
            id="certificate",
        ),
        pytest.param(
            aiohttp.ClientConnectorSSLError(MagicMock(), ssl.SSLError("wrong version")),
            id="handshake",
        ),
    ],
)
@pytest.mark.asyncio
async def test_async_does_not_retry_tls_errors(sleeps, monkeypatch, error):
    request = AsyncMock(side_effect=error)
    monkeypatch.setattr(AsyncRESTClientObject, "request", request)
    async with AsyncApiClient(make_configuration("https://fga.example")) as client:
        with pytest.raises(type(error)):
            await client.call_api("/check", "POST", **CALL_ARGS)

    request.assert_awaited_once()
    assert sleeps == []


# aiohttp would otherwise resend the GET once on its own, outside retry_params.
@aiohttp_replay_is_configurable
@pytest.mark.asyncio
async def test_async_disables_aiohttp_replay(server, sleeps):
    server.actions.append("drop")
    async with AsyncApiClient(make_configuration(server.url)) as client:
        with pytest.raises(aiohttp.ServerDisconnectedError):
            await client.call_api(
                "/stores", "GET", _retry_params=RetryParams(max_retry=0), **CALL_ARGS
            )

    assert server.requests == ["GET"]
    assert sleeps == []


# max_retry=1 allows two token requests; the default would allow four.
def test_sync_token_request_uses_client_retry_params(server, sleeps):
    server.actions.extend(["drop"] * 4)
    credentials = Credentials(
        method="client_credentials",
        configuration=CredentialConfiguration(
            client_id="client-id",
            client_secret="client-secret",
            api_issuer=f"{server.url}/oauth/token",
            api_audience="audience",
        ),
    )
    configuration = make_configuration(server.url, credentials=credentials)
    with SyncApiClient(configuration) as client:
        with pytest.raises(urllib3.exceptions.ProtocolError):
            SyncOpenFgaApi(client).list_stores()

    assert server.requests == ["POST", "POST"]


@pytest.mark.parametrize("failure", ["drop", "503"])
@pytest.mark.asyncio
async def test_async_stream_retries_until_connected(server, sleeps, failure):
    server.actions.append(failure)
    async with AsyncApiClient(make_configuration(server.url)) as client:
        stream = await client.call_api("/stream", "POST", _streaming=True, **CALL_ARGS)
        received = [obj async for obj in stream]

    assert received == OBJECTS
    assert server.requests == ["POST", "POST"]


@pytest.mark.parametrize("failure", ["drop", "503"])
def test_sync_stream_retries_until_connected(server, sleeps, failure):
    server.actions.append(failure)
    with SyncApiClient(make_configuration(server.url)) as client:
        stream = client.call_api("/stream", "POST", _streaming=True, **CALL_ARGS)
        received = list(stream)

    assert received == OBJECTS
    assert server.requests == ["POST", "POST"]


# Once the body has started, a failure raises to the caller instead of
# restarting the stream, which would repeat the objects already yielded.
@pytest.mark.asyncio
async def test_async_stream_raises_without_retry_once_connected(server, sleeps):
    server.actions.append("truncate")
    received = []
    async with AsyncApiClient(make_configuration(server.url)) as client:
        stream = await client.call_api("/stream", "POST", _streaming=True, **CALL_ARGS)
        with pytest.raises(aiohttp.ClientPayloadError):
            async for obj in stream:
                received.append(obj)

    assert received == OBJECTS[:1]
    assert server.requests == ["POST"]
    assert sleeps == []


def test_sync_stream_raises_without_retry_once_connected(server, sleeps):
    server.actions.append("truncate")
    received = []
    with SyncApiClient(make_configuration(server.url)) as client:
        stream = client.call_api("/stream", "POST", _streaming=True, **CALL_ARGS)
        with pytest.raises(urllib3.exceptions.ProtocolError):
            received.extend(stream)

    assert received == OBJECTS[:1]
    assert server.requests == ["POST"]
    assert sleeps == []


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
        stream = client.execute_streamed_api_request(
            operation_name="StreamedListObjects",
            method="POST",
            path="/stores/{store_id}/streamed-list-objects",
            path_params={"store_id": STORE_ID},
            body={},
        )
        first = await anext(stream)
        await stream.aclose()

        assert first == OBJECTS[0]
        assert releases == [1]


def test_sync_closing_streamed_list_objects_releases_response(server, releases):
    with SyncOpenFgaClient(make_client_configuration(server.url)) as client:
        stream = client.streamed_list_objects(LIST_OBJECTS)
        first = next(stream)
        stream.close()

        assert first.object == "document:0"
        assert releases[0] >= 1
