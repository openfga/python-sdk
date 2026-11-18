from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
import urllib3

from openfga_sdk.api_client import ApiClient as AsyncApiClient
from openfga_sdk.configuration import Configuration, RetryParams
from openfga_sdk.sync.api_client import ApiClient as SyncApiClient


BACKOFF = 0.125
IMF_FIXDATE = "%a, %d %b %Y %H:%M:%S GMT"


def http_date(**delta):
    return (datetime.now(timezone.utc) + timedelta(**delta)).strftime(IMF_FIXDATE)


# urllib3 retries idempotent methods like GET on its own unless the SDK stops it.
http_methods = pytest.mark.parametrize("method", ["GET", "POST"])

retry_after_cases = pytest.mark.parametrize(
    "status,retry_after,expected_wait",
    [
        (429, "0", BACKOFF),
        (429, "1", 1),
        (429, "10", 10),
        (429, "31", 31),
        (429, "60", 60),
        (429, "1800", 1800),
        (429, "-1", BACKOFF),
        (429, "1801", BACKOFF),
        (429, "not-a-date", BACKOFF),
        (503, "60", 60),
    ],
)


@pytest.fixture
def retry_server(status, retry_after):
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def _respond(self):
            requests.append(self.path)
            self.send_response(status if len(requests) == 1 else 200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Retry-After", retry_after)
            self.send_header("Content-Length", "2")
            self.end_headers()
            self.wfile.write(b"{}")

        do_GET = do_POST = _respond

    with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
        thread = Thread(
            target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True
        )
        thread.start()
        try:
            yield f"http://127.0.0.1:{server.server_port}", requests
        finally:
            server.shutdown()
            thread.join()


@http_methods
@retry_after_cases
@pytest.mark.asyncio
async def test_async_retry_after_over_http(retry_server, method, expected_wait):
    url, requests = retry_server
    configuration = Configuration(
        api_url=url, retry_params=RetryParams(max_retry=1, max_wait_in_sec=1)
    )
    with (
        patch("openfga_sdk.api_client.random_time", return_value=BACKOFF),
        patch("asyncio.sleep", new_callable=AsyncMock) as sleep,
    ):
        async with AsyncApiClient(configuration) as client:
            result = await client.call_api(
                "/retry", method, response_types_map={}, _return_http_data_only=True
            )

    assert result is None
    assert requests == ["/retry", "/retry"]
    sleep.assert_awaited_once_with(expected_wait)


@http_methods
@retry_after_cases
def test_sync_retry_after_over_http(retry_server, method, expected_wait):
    url, requests = retry_server
    configuration = Configuration(
        api_url=url, retry_params=RetryParams(max_retry=1, max_wait_in_sec=1)
    )
    with (
        patch("openfga_sdk.sync.api_client.random_time", return_value=BACKOFF),
        patch("time.sleep") as sleep,
        patch.object(urllib3.Retry, "sleep") as urllib3_sleep,
        SyncApiClient(configuration) as client,
    ):
        result = client.call_api(
            "/retry", method, response_types_map={}, _return_http_data_only=True
        )

    assert result is None
    assert requests == ["/retry", "/retry"]
    sleep.assert_called_once_with(expected_wait)
    urllib3_sleep.assert_not_called()


@pytest_asyncio.fixture(params=["async", "sync"])
async def parse_retry_after(request):
    configuration = Configuration(api_url="http://localhost:8080")
    if request.param == "async":
        async with AsyncApiClient(configuration) as client:
            yield lambda value: client._parse_retry_after_header({"retry-after": value})
    else:
        with SyncApiClient(configuration) as client:
            yield lambda value: client._parse_retry_after_header({"retry-after": value})


# HTTP-date formats a recipient must accept per RFC 9110 section 5.6.7.
@pytest.mark.parametrize(
    "format_date",
    [
        lambda d: d.strftime(IMF_FIXDATE),
        lambda d: d.strftime("%A, %d-%b-%y %H:%M:%S GMT"),
        lambda d: f"{d:%a %b} {d.day:2} {d:%H:%M:%S %Y}",  # space-padded day
    ],
    ids=["imf-fixdate", "rfc850", "asctime"],
)
@pytest.mark.asyncio
async def test_parse_retry_after_http_date(parse_retry_after, format_date):
    retry_at = datetime.now(timezone.utc) + timedelta(seconds=60)

    wait = parse_retry_after(format_date(retry_at))

    assert 50 <= wait <= 60


@pytest.mark.parametrize(
    "value",
    [
        "1.5",
        "5s",
        "Wed, 01 Jan 2025 00:00:00 +999999999999999999",
        pytest.param(http_date(seconds=-5), id="date-in-past"),
        pytest.param(http_date(hours=1), id="date-above-max"),
    ],
)
@pytest.mark.asyncio
async def test_parse_retry_after_rejects_invalid(parse_retry_after, value):
    with pytest.raises(ValueError):
        parse_retry_after(value)
