import socket
import ssl

from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest
import urllib3

from openfga_sdk.api_client import ApiClient as AsyncApiClient
from openfga_sdk.configuration import Configuration, RetryParams
from openfga_sdk.credentials import CredentialConfiguration, Credentials
from openfga_sdk.exceptions import ServiceException
from openfga_sdk.rest import RESTClientObject as AsyncRESTClientObject
from openfga_sdk.sync.api_client import ApiClient as SyncApiClient
from openfga_sdk.sync.open_fga_api import OpenFgaApi as SyncOpenFgaApi


CALL_ARGS = {"response_types_map": {}, "_return_http_data_only": True}
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
    assert sleeps == [server.retry_after]
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
