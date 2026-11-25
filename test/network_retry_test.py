import json
import socket
import ssl

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest
import urllib3

from openfga_sdk.api_client import ApiClient as AsyncApiClient
from openfga_sdk.configuration import Configuration, RetryParams
from openfga_sdk.credentials import CredentialConfiguration, Credentials
from openfga_sdk.sync.api_client import ApiClient as SyncApiClient
from openfga_sdk.sync.open_fga_api import OpenFgaApi as SyncOpenFgaApi
from openfga_sdk.telemetry.attributes import TelemetryAttributes
from openfga_sdk.telemetry.metrics import TelemetryMetrics


CALL_ARGS = {"response_types_map": {}, "_return_http_data_only": True}
OBJECTS = [{"result": {"object": f"document:{i}"}} for i in range(3)]
NDJSON = b"".join(json.dumps(obj).encode() + b"\n" for obj in OBJECTS)

# The configured max_retry=1 allows two attempts; the per-call override allows one.
exhausted_cases = pytest.mark.parametrize(
    "retry_params,attempts",
    [(None, 2), (RetryParams(max_retry=0), 1)],
    ids=["retries-exhausted", "retries-disabled-per-call"],
)


def configuration(url, **kwargs):
    return Configuration(api_url=url, retry_params=RetryParams(max_retry=1), **kwargs)


@pytest.fixture
def server():
    """
    Replies to each request with the next queued action, then with 200:
    "drop" closes the connection without a response, "503" sends a 503 and
    "truncate" closes the connection after the first chunk of the body.
    """
    actions, requests = [], []

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, format, *args):
            pass

        def _respond(self):
            self.rfile.read(int(self.headers.get("Content-Length", 0)))
            requests.append(self.command)
            action = actions.pop(0) if actions else "200"
            if action == "drop":
                self.close_connection = True
                return

            self.send_response(503 if action == "503" else 200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Transfer-Encoding", "chunked")
            self.end_headers()
            for line in (b"{}" if action == "503" else NDJSON).splitlines(True):
                self.wfile.write(b"%x\r\n%s\r\n" % (len(line), line))
                if action == "truncate":
                    self.close_connection = True
                    return
            self.wfile.write(b"0\r\n\r\n")

        do_GET = do_POST = _respond

    with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as httpd:
        thread = Thread(
            target=httpd.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True
        )
        thread.start()
        try:
            yield f"http://127.0.0.1:{httpd.server_port}", actions, requests
        finally:
            httpd.shutdown()
            thread.join()


@pytest.fixture
def resend_counts():
    """The http.request.resend_count of every request metric recorded."""
    counts = []

    def request(self, attributes, configuration=None):
        counts.append(attributes[TelemetryAttributes.http_request_resend_count])

    with patch.object(TelemetryMetrics, "request", request):
        yield counts


@pytest.mark.asyncio
async def test_async_retries_dropped_connection(server, resend_counts):
    url, actions, requests = server
    actions.append("drop")
    with patch("asyncio.sleep", new_callable=AsyncMock) as sleep:
        async with AsyncApiClient(configuration(url)) as client:
            await client.call_api("/check", "POST", **CALL_ARGS)

    assert requests == ["POST", "POST"]
    assert resend_counts == [0, 1]
    sleep.assert_awaited_once()


def test_sync_retries_dropped_connection(server, resend_counts):
    url, actions, requests = server
    actions.append("drop")
    with patch("time.sleep") as sleep, SyncApiClient(configuration(url)) as client:
        client.call_api("/check", "POST", **CALL_ARGS)

    assert requests == ["POST", "POST"]
    assert resend_counts == [0, 1]
    sleep.assert_called_once()


@exhausted_cases
@pytest.mark.asyncio
async def test_async_raises_network_error_when_out_of_retries(
    server, retry_params, attempts
):
    url, actions, requests = server
    actions.extend(["drop"] * attempts)
    with patch("asyncio.sleep", new_callable=AsyncMock):
        async with AsyncApiClient(configuration(url)) as client:
            with pytest.raises(aiohttp.ServerDisconnectedError):
                await client.call_api(
                    "/check", "POST", _retry_params=retry_params, **CALL_ARGS
                )

    assert requests == ["POST"] * attempts


# urllib3 would otherwise resend the GET on its own.
@exhausted_cases
def test_sync_raises_network_error_when_out_of_retries(server, retry_params, attempts):
    url, actions, requests = server
    actions.extend(["drop"] * attempts)
    with (
        patch("time.sleep"),
        SyncApiClient(configuration(url)) as client,
        pytest.raises(urllib3.exceptions.ProtocolError),
    ):
        client.call_api("/stores", "GET", _retry_params=retry_params, **CALL_ARGS)

    assert requests == ["GET"] * attempts


def test_sync_retries_unreachable_proxy():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]

    config = configuration("http://fga.example")
    config.proxy = f"http://127.0.0.1:{port}"
    with (
        patch("time.sleep") as sleep,
        SyncApiClient(config) as client,
        pytest.raises(urllib3.exceptions.ProxyError),
    ):
        client.call_api("/check", "POST", **CALL_ARGS)

    sleep.assert_called_once()


@pytest.mark.asyncio
async def test_async_does_not_retry_certificate_errors():
    error = aiohttp.ClientConnectorCertificateError(
        MagicMock(), ssl.SSLCertVerificationError("certificate verify failed")
    )
    with (
        patch("asyncio.sleep", new_callable=AsyncMock) as sleep,
        patch(
            "openfga_sdk.rest.RESTClientObject.request", side_effect=error
        ) as request,
    ):
        async with AsyncApiClient(configuration("https://fga.example")) as client:
            with pytest.raises(aiohttp.ClientConnectorCertificateError):
                await client.call_api("/check", "POST", **CALL_ARGS)

    request.assert_called_once()
    sleep.assert_not_awaited()


# max_retry=1 allows two token requests; the default would allow four.
def test_sync_token_request_uses_client_retry_params(server):
    url, actions, requests = server
    actions.extend(["drop"] * 4)
    credentials = Credentials(
        method="client_credentials",
        configuration=CredentialConfiguration(
            client_id="client-id",
            client_secret="client-secret",
            api_issuer=f"{url}/oauth/token",
            api_audience="audience",
        ),
    )
    with (
        patch("time.sleep"),
        SyncApiClient(configuration(url, credentials=credentials)) as client,
        pytest.raises(urllib3.exceptions.ProtocolError),
    ):
        SyncOpenFgaApi(client).list_stores()

    assert requests == ["POST", "POST"]


@pytest.mark.parametrize("failure", ["drop", "503"])
@pytest.mark.asyncio
async def test_async_stream_retries_until_connected(server, failure):
    url, actions, requests = server
    actions.append(failure)
    with patch("asyncio.sleep", new_callable=AsyncMock):
        async with AsyncApiClient(configuration(url)) as client:
            stream = await client.call_api(
                "/stream", "POST", _streaming=True, **CALL_ARGS
            )
            received = [obj async for obj in stream]

    assert received == OBJECTS
    assert requests == ["POST", "POST"]


@pytest.mark.parametrize("failure", ["drop", "503"])
def test_sync_stream_retries_until_connected(server, failure):
    url, actions, requests = server
    actions.append(failure)
    with patch("time.sleep"), SyncApiClient(configuration(url)) as client:
        stream = client.call_api("/stream", "POST", _streaming=True, **CALL_ARGS)
        received = list(stream)

    assert received == OBJECTS
    assert requests == ["POST", "POST"]


@pytest.mark.asyncio
async def test_async_stream_raises_without_retry_once_connected(server):
    url, actions, requests = server
    actions.append("truncate")
    with patch("asyncio.sleep", new_callable=AsyncMock):
        async with AsyncApiClient(configuration(url)) as client:
            stream = await client.call_api(
                "/stream", "POST", _streaming=True, **CALL_ARGS
            )
            with pytest.raises(aiohttp.ClientPayloadError):
                [obj async for obj in stream]

    assert requests == ["POST"]


def test_sync_stream_raises_without_retry_once_connected(server):
    url, actions, requests = server
    actions.append("truncate")
    with patch("time.sleep"), SyncApiClient(configuration(url)) as client:
        stream = client.call_api("/stream", "POST", _streaming=True, **CALL_ARGS)
        with pytest.raises(urllib3.exceptions.ProtocolError):
            list(stream)

    assert requests == ["POST"]
