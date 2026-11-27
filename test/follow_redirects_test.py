import threading

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from openfga_sdk import rest
from openfga_sdk.client import ClientConfiguration
from openfga_sdk.configuration import Configuration
from openfga_sdk.exceptions import ApiException
from openfga_sdk.sync import rest as sync_rest


class _RedirectHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/target":
            body = b'{"ok":true}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(302)
        self.send_header("Location", "/target")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, *args):
        pass


@pytest.fixture
def redirect_server():
    server = ThreadingHTTPServer(("127.0.0.1", 0), _RedirectHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()
    server.server_close()


def _config(follow_redirects=None):
    if follow_redirects is None:
        return Configuration(api_url="http://127.0.0.1")
    return Configuration(api_url="http://127.0.0.1", follow_redirects=follow_redirects)


def test_follow_redirects_defaults_to_true():
    assert Configuration().follow_redirects is True
    assert ClientConfiguration().follow_redirects is True


def test_client_configuration_passes_follow_redirects():
    assert ClientConfiguration(follow_redirects=False).follow_redirects is False


def test_sync_follows_redirects_by_default(redirect_server):
    client = sync_rest.RESTClientObject(_config())
    try:
        resp = client.request("GET", f"{redirect_server}/start")
        assert resp.status == 200
        assert resp.data == b'{"ok":true}'
    finally:
        client.close()


def test_sync_raises_on_redirect_when_disabled(redirect_server):
    client = sync_rest.RESTClientObject(_config(follow_redirects=False))
    try:
        with pytest.raises(ApiException) as err:
            client.request("GET", f"{redirect_server}/start")
        assert err.value.status == 302
    finally:
        client.close()


@pytest.mark.asyncio
async def test_async_follows_redirects_by_default(redirect_server):
    client = rest.RESTClientObject(_config())
    try:
        resp = await client.request("GET", f"{redirect_server}/start")
        assert resp.status == 200
        assert resp.data == b'{"ok":true}'
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_async_raises_on_redirect_when_disabled(redirect_server):
    client = rest.RESTClientObject(_config(follow_redirects=False))
    try:
        with pytest.raises(ApiException) as err:
            await client.request("GET", f"{redirect_server}/start")
        assert err.value.status == 302
    finally:
        await client.close()
