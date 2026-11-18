from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio

from openfga_sdk.api_client import ApiClient as AsyncApiClient
from openfga_sdk.configuration import Configuration, RetryParams
from openfga_sdk.sync.api_client import ApiClient as SyncApiClient


BACKOFF = 0.125

# GET is idempotent, so urllib3 would retry it (and honor Retry-After) on its
# own unless the SDK disables that; POST is never retried by urllib3.
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
        SyncApiClient(configuration) as client,
    ):
        result = client.call_api(
            "/retry", method, response_types_map={}, _return_http_data_only=True
        )

    assert result is None
    assert requests == ["/retry", "/retry"]
    sleep.assert_called_once_with(expected_wait)


@pytest_asyncio.fixture(params=["async", "sync"])
async def parse_retry_after(request):
    configuration = Configuration(api_url="http://localhost:8080")
    if request.param == "async":
        async with AsyncApiClient(configuration) as client:
            yield lambda value: client._parse_retry_after_header({"retry-after": value})
    else:
        with SyncApiClient(configuration) as client:
            yield lambda value: client._parse_retry_after_header({"retry-after": value})


# The three HTTP-date formats a recipient must accept per RFC 9110 section 5.6.7.
@pytest.mark.parametrize(
    "http_date_format",
    [
        "%a, %d %b %Y %H:%M:%S GMT",  # IMF-fixdate
        "%A, %d-%b-%y %H:%M:%S GMT",  # obsolete RFC 850
        "%a %b %d %H:%M:%S %Y",  # obsolete asctime (implicitly GMT)
    ],
    ids=["imf-fixdate", "rfc850", "asctime"],
)
@pytest.mark.asyncio
async def test_parse_retry_after_http_date(parse_retry_after, http_date_format):
    retry_at = datetime.now(timezone.utc) + timedelta(seconds=60)

    wait = parse_retry_after(retry_at.strftime(http_date_format))

    assert 59 <= wait <= 60


@pytest.mark.parametrize(
    "value",
    [
        "0",
        "-1",
        "1801",
        "1.5",
        "5s",
        "not-a-date",
        (datetime.now(timezone.utc) - timedelta(seconds=5)).strftime(
            "%a, %d %b %Y %H:%M:%S GMT"
        ),
        (datetime.now(timezone.utc) + timedelta(hours=1)).strftime(
            "%a, %d %b %Y %H:%M:%S GMT"
        ),
    ],
    ids=[
        "zero",
        "negative",
        "above-max",
        "fractional",
        "unit-suffix",
        "garbage",
        "date-in-past",
        "date-above-max",
    ],
)
@pytest.mark.asyncio
async def test_parse_retry_after_rejects_out_of_range_or_invalid(
    parse_retry_after, value
):
    with pytest.raises(ValueError):
        parse_retry_after(value)
