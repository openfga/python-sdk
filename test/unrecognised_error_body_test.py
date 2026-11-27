"""Regression tests: error responses the client doesn't recognise must raise ApiException.

An ApiException for a status outside the mapped error types keeps its body as
a raw str, and TelemetryAttributes.fromResponse must tolerate that instead of
calling .get() on it. A mapped status whose body is not JSON, or is JSON that
doesn't fit the expected model, must keep the raw body instead of escaping.
"""

import asyncio
import threading

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from openfga_sdk.api_client import ApiClient as AsyncApiClient
from openfga_sdk.configuration import Configuration, RetryParams
from openfga_sdk.exceptions import ApiException
from openfga_sdk.sync.api_client import ApiClient as SyncApiClient
from openfga_sdk.telemetry.attributes import TelemetryAttributes


RESPONSE_TYPES = {404: "PathUnknownErrorMessageResponse"}

# (status, body, content type, expected body on the raised exception)
ERROR_RESPONSES = [
    pytest.param(
        408, b'{"code":"timeout"}', "application/json", id="unmapped-408-json"
    ),
    pytest.param(413, b"Payload Too Large", "text/plain", id="unmapped-413-text"),
    pytest.param(404, b"<html>Not Found</html>", "text/html", id="mapped-404-html"),
    pytest.param(404, b"[]", "application/json", id="mapped-404-json-list"),
    pytest.param(404, b'"not found"', "application/json", id="mapped-404-json-string"),
]


@pytest.fixture
def serve():
    """Starts a local server that answers every GET with the given response."""
    servers = []

    def start(status, body, content_type):
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                pass

            def do_GET(self):
                self.send_response(status)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        servers.append(httpd)
        return f"http://127.0.0.1:{httpd.server_port}"

    yield start
    for httpd in servers:
        httpd.shutdown()
        httpd.server_close()


def make_configuration(url):
    # max_retry=0 so that every error is raised on the first attempt.
    return Configuration(api_url=url, retry_params=RetryParams(max_retry=0))


def assert_raw_api_exception(exc, status, body):
    assert exc.status == status
    assert exc.body == body.decode()
    assert exc.parsed_exception is None


@pytest.mark.parametrize("status,body,content_type", ERROR_RESPONSES)
def test_sync_client_raises_api_exception(serve, status, body, content_type):
    url = serve(status, body, content_type)
    with SyncApiClient(make_configuration(url)) as client:
        with pytest.raises(ApiException) as info:
            client.call_api(
                "/stores",
                "GET",
                response_types_map=RESPONSE_TYPES,
                _return_http_data_only=True,
            )

    assert_raw_api_exception(info.value, status, body)


@pytest.mark.parametrize("status,body,content_type", ERROR_RESPONSES)
def test_async_client_raises_api_exception(serve, status, body, content_type):
    url = serve(status, body, content_type)

    async def call():
        async with AsyncApiClient(make_configuration(url)) as client:
            await client.call_api(
                "/stores",
                "GET",
                response_types_map=RESPONSE_TYPES,
                _return_http_data_only=True,
            )

    with pytest.raises(ApiException) as info:
        asyncio.run(call())

    assert_raw_api_exception(info.value, status, body)


def test_fromResponse_accepts_unmapped_error_with_str_body():
    exc = ApiException(status=408, reason="Request Timeout")
    exc.body = '{"code":"timeout"}'

    attributes = TelemetryAttributes.fromResponse(response=exc)

    assert attributes[TelemetryAttributes.http_response_status_code] == 408
