from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from unittest.mock import AsyncMock, patch

import pytest

from openfga_sdk.api_client import ApiClient as AsyncApiClient
from openfga_sdk.configuration import Configuration, RetryParams
from openfga_sdk.sync.api_client import ApiClient as SyncApiClient


retry_after_cases = pytest.mark.parametrize(
    "status,retry_after,expected_wait",
    [
        (429, "0", 0),
        (429, "1", 1),
        (429, "10", 10),
        (429, "31", 31),
        (429, "60", 60),
        (429, "1800", 1800),
        (429, "-1", 0.125),
        (429, "1801", 0.125),
        (429, "not-a-date", 0.125),
        (503, "60", 60),
    ],
)


@pytest.fixture
def retry_server(status, retry_after):
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            requests.append(self.path)
            self.send_response(status if len(requests) == 1 else 200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Retry-After", retry_after)
            self.send_header("Content-Length", "2")
            self.end_headers()
            self.wfile.write(b"{}")

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


@retry_after_cases
@pytest.mark.asyncio
async def test_async_retry_after_over_http(retry_server, expected_wait):
    url, requests = retry_server
    configuration = Configuration(
        api_url=url, retry_params=RetryParams(max_retry=1, max_wait_in_sec=1)
    )
    with (
        patch("openfga_sdk.api_client.random_time", return_value=0.125),
        patch("asyncio.sleep", new_callable=AsyncMock) as sleep,
    ):
        async with AsyncApiClient(configuration) as client:
            result = await client.call_api(
                "/retry", "POST", response_types_map={}, _return_http_data_only=True
            )

    assert result is None
    assert requests == ["/retry", "/retry"]
    sleep.assert_awaited_once_with(expected_wait)


@retry_after_cases
def test_sync_retry_after_over_http(retry_server, expected_wait):
    url, requests = retry_server
    configuration = Configuration(
        api_url=url, retry_params=RetryParams(max_retry=1, max_wait_in_sec=1)
    )
    with (
        patch("openfga_sdk.sync.api_client.random_time", return_value=0.125),
        patch("time.sleep") as sleep,
        SyncApiClient(configuration) as client,
    ):
        result = client.call_api(
            "/retry", "POST", response_types_map={}, _return_http_data_only=True
        )

    assert result is None
    assert requests == ["/retry", "/retry"]
    sleep.assert_called_once_with(expected_wait)
