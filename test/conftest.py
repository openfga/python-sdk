import asyncio
import json
import time

from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Event, Thread

import aiohttp
import pytest
import urllib3

from openfga_sdk.telemetry.attributes import TelemetryAttributes
from openfga_sdk.telemetry.metrics import TelemetryMetrics


@dataclass
class FakeServer:
    """A local HTTP server that replies to each request with a scripted action."""

    url: str
    objects: list[dict]
    retry_after: int
    actions: list[str] = field(default_factory=list)
    requests: list[str] = field(default_factory=list)


@pytest.fixture
def server():
    """
    Replies to each request with the next queued action, then with 200 and
    ``server.objects`` as NDJSON: "drop" closes the connection without a
    response, "hang" never responds, "503" sends a 503 with a Retry-After
    header and "truncate" closes the connection after the first chunk.
    """
    stopping = Event()
    objects = [{"result": {"object": f"document:{i}"}} for i in range(3)]
    ndjson = b"".join(json.dumps(obj).encode() + b"\n" for obj in objects)

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
                self.send_header("Retry-After", str(fake.retry_after))
            self.end_headers()
            for line in (b"{}" if action == "503" else ndjson).splitlines(True):
                self.wfile.write(b"%x\r\n%s\r\n" % (len(line), line))
                if action == "truncate":
                    self.close_connection = True
                    return
            self.wfile.write(b"0\r\n\r\n")

        do_GET = do_POST = _respond

    with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as httpd:
        fake = FakeServer(
            url=f"http://127.0.0.1:{httpd.server_port}", objects=objects, retry_after=7
        )
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
    """Records "aiohttp" or "urllib3" each time a response is handed back to its pool."""
    events = []
    release = aiohttp.ClientResponse.release
    release_conn = urllib3.response.HTTPResponse.release_conn

    def recording_release(self):
        events.append("aiohttp")
        return release(self)

    def recording_release_conn(self):
        events.append("urllib3")
        return release_conn(self)

    monkeypatch.setattr(aiohttp.ClientResponse, "release", recording_release)
    monkeypatch.setattr(
        urllib3.response.HTTPResponse, "release_conn", recording_release_conn
    )
    return events


@pytest.fixture
def resend_counts(monkeypatch):
    """The http.request.resend_count of every request metric recorded."""
    counts = []

    def request(self, attributes, configuration=None):
        counts.append(attributes[TelemetryAttributes.http_request_resend_count])

    monkeypatch.setattr(TelemetryMetrics, "request", request)
    return counts
