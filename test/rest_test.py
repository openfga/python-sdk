import json

from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

from openfga_sdk.exceptions import (
    ApiException,
    ForbiddenException,
    NotFoundException,
    RateLimitExceededError,
    ServiceException,
    UnauthorizedException,
    ValidationException,
)
from openfga_sdk.rest import RESTClientObject, RESTResponse


@pytest.mark.asyncio
async def test_restresponse_init():
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.reason = "OK"

    resp_data = b'{"test":"data"}'
    rest_resp = RESTResponse(mock_resp, resp_data)

    assert rest_resp.status == 200
    assert rest_resp.reason == "OK"
    assert rest_resp.data == resp_data
    assert rest_resp.response == mock_resp


def test_restresponse_getheaders():
    mock_resp = MagicMock()
    mock_resp.headers = {"Content-Type": "application/json", "X-Testing": "true"}
    rest_resp = RESTResponse(mock_resp, b"")
    headers = rest_resp.getheaders()
    assert headers["Content-Type"] == "application/json"
    assert headers["X-Testing"] == "true"


def test_restresponse_getheader():
    mock_resp = MagicMock()
    mock_resp.headers = {"Content-Type": "application/json"}
    rest_resp = RESTResponse(mock_resp, b"")
    val = rest_resp.getheader("Content-Type")
    missing = rest_resp.getheader("X-Not-Here", default="fallback")
    assert val == "application/json"
    assert missing == "fallback"


@pytest.mark.asyncio
async def test_build_request_json_body():
    mock_config = MagicMock()
    mock_config.ssl_ca_cert = None
    mock_config.cert_file = None
    mock_config.key_file = None
    mock_config.verify_ssl = True
    mock_config.connection_pool_maxsize = 4
    mock_config.proxy = None
    mock_config.proxy_headers = None
    mock_config.timeout_millisec = 5000

    client = RESTClientObject(configuration=mock_config)
    req_args = await client.build_request(
        method="POST",
        url="http://example.com/test",
        body={"foo": "bar"},
        headers={"Content-Type": "application/json"},
    )
    assert req_args["method"] == "POST"
    assert req_args["url"] == "http://example.com/test"
    assert req_args["headers"]["Content-Type"] == "application/json"
    assert json.loads(req_args["data"]) == {"foo": "bar"}


@pytest.mark.asyncio
async def test_build_request_form_data():
    mock_config = MagicMock()
    mock_config.ssl_ca_cert = None
    mock_config.cert_file = None
    mock_config.key_file = None
    mock_config.verify_ssl = True
    mock_config.connection_pool_maxsize = 4
    mock_config.proxy = None
    mock_config.proxy_headers = None
    mock_config.timeout_millisec = 5000

    client = RESTClientObject(configuration=mock_config)
    req_args = await client.build_request(
        method="POST",
        url="http://example.com/upload",
        post_params=[("file", ("filename.txt", b"contents", "text/plain"))],
        headers={"Content-Type": "multipart/form-data"},
    )
    assert req_args["method"] == "POST"
    assert req_args["url"] == "http://example.com/upload"
    assert "Content-Type" not in req_args["headers"]
    assert "data" in req_args


@pytest.mark.asyncio
async def test_build_request_timeout():
    mock_config = MagicMock()
    mock_config.ssl_ca_cert = None
    mock_config.cert_file = None
    mock_config.key_file = None
    mock_config.verify_ssl = True
    mock_config.connection_pool_maxsize = 4
    mock_config.proxy = None
    mock_config.proxy_headers = None
    mock_config.timeout_millisec = 5000

    client = RESTClientObject(configuration=mock_config)
    req_args = await client.build_request(
        method="GET",
        url="http://example.com",
        _request_timeout=10.0,
    )
    assert req_args["timeout"] == 10.0


@pytest.mark.asyncio
async def test_handle_response_exception_success():
    mock_config = MagicMock()
    mock_config.ssl_ca_cert = None
    mock_config.cert_file = None
    mock_config.key_file = None
    mock_config.verify_ssl = True
    mock_config.connection_pool_maxsize = 4
    mock_config.proxy = None
    mock_config.proxy_headers = None
    mock_config.timeout_millisec = 5000

    client = RESTClientObject(configuration=mock_config)
    mock_response = MagicMock()
    mock_response.status = 200
    await client.handle_response_exception(mock_response)


@pytest.mark.parametrize(
    "status, exc",
    [
        (400, ValidationException),
        (401, UnauthorizedException),
        (403, ForbiddenException),
        (404, NotFoundException),
        (429, RateLimitExceededError),
        (500, ServiceException),
        (418, ApiException),
    ],
)
@pytest.mark.asyncio
async def test_handle_response_exception_error(status, exc):
    mock_config = MagicMock()
    mock_config.ssl_ca_cert = None
    mock_config.cert_file = None
    mock_config.key_file = None
    mock_config.verify_ssl = True
    mock_config.connection_pool_maxsize = 4
    mock_config.proxy = None
    mock_config.proxy_headers = None
    mock_config.timeout_millisec = 5000

    client = RESTClientObject(configuration=mock_config)
    mock_response = MagicMock()
    mock_response.status = status

    with pytest.raises(exc):
        await client.handle_response_exception(mock_response)


@pytest.mark.asyncio
async def test_handle_response_exception_reads_data():
    mock_config = MagicMock()
    mock_config.ssl_ca_cert = None
    mock_config.cert_file = None
    mock_config.key_file = None
    mock_config.verify_ssl = True
    mock_config.connection_pool_maxsize = 4
    mock_config.proxy = None
    mock_config.proxy_headers = None
    mock_config.timeout_millisec = 5000

    client = RESTClientObject(configuration=mock_config)

    mock_response = MagicMock(spec=aiohttp.ClientResponse)
    mock_response.status = 400
    mock_response.read = AsyncMock(return_value=b'{"error":"bad"}')

    with pytest.raises(ValidationException):
        await client.handle_response_exception(mock_response)

    mock_response.read.assert_awaited_once()
    assert mock_response.data == b'{"error":"bad"}'


@pytest.mark.asyncio
async def test_close():
    mock_config = MagicMock()
    mock_config.ssl_ca_cert = None
    mock_config.cert_file = None
    mock_config.key_file = None
    mock_config.verify_ssl = True
    mock_config.connection_pool_maxsize = 4
    mock_config.proxy = None
    mock_config.proxy_headers = None
    mock_config.timeout_millisec = 5000

    client = RESTClientObject(configuration=mock_config)

    mock_session = MagicMock()
    mock_session.close = AsyncMock()
    client.pool_manager = mock_session

    await client.close()

    mock_session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_request_preload_content():
    # Mock config
    mock_config = MagicMock()
    mock_config.ssl_ca_cert = None
    mock_config.cert_file = None
    mock_config.key_file = None
    mock_config.verify_ssl = True
    mock_config.connection_pool_maxsize = 4
    mock_config.proxy = None
    mock_config.proxy_headers = None
    mock_config.timeout_millisec = 5000

    client = RESTClientObject(configuration=mock_config)

    mock_session = MagicMock()
    client.pool_manager = mock_session

    mock_raw_response = MagicMock()
    mock_raw_response.status = 200
    mock_raw_response.reason = "OK"
    mock_raw_response.read = AsyncMock(return_value=b'{"some":"data"}')
    mock_session.request = AsyncMock(return_value=mock_raw_response)

    resp = await client.request(
        method="GET", url="http://example.com", _preload_content=True
    )

    mock_session.request.assert_awaited_once()
    mock_raw_response.read.assert_awaited_once()

    assert resp.status == 200
    assert resp.reason == "OK"
    assert resp.data == b'{"some":"data"}'


@pytest.mark.asyncio
async def test_request_no_preload_content():
    mock_config = MagicMock()
    mock_config.ssl_ca_cert = None
    mock_config.cert_file = None
    mock_config.key_file = None
    mock_config.verify_ssl = True
    mock_config.connection_pool_maxsize = 4
    mock_config.proxy = None
    mock_config.proxy_headers = None
    mock_config.timeout_millisec = 5000

    client = RESTClientObject(configuration=mock_config)

    mock_session = MagicMock()
    client.pool_manager = mock_session

    mock_raw_response = MagicMock()
    mock_raw_response.status = 200
    mock_raw_response.reason = "OK"
    mock_raw_response.read = AsyncMock(return_value=b"unused")
    mock_session.request = AsyncMock(return_value=mock_raw_response)

    resp = await client.request(
        method="GET", url="http://example.com", _preload_content=False
    )

    mock_session.request.assert_awaited_once()

    assert resp == mock_raw_response
    assert resp.status == 200
    assert resp.reason == "OK"


@pytest.mark.asyncio
async def test_stream_happy_path():
    mock_config = MagicMock()
    mock_config.ssl_ca_cert = None
    mock_config.cert_file = None
    mock_config.key_file = None
    mock_config.verify_ssl = True
    mock_config.connection_pool_maxsize = 4
    mock_config.proxy = None
    mock_config.proxy_headers = None
    mock_config.timeout_millisec = 5000

    client = RESTClientObject(configuration=mock_config)
    mock_session = MagicMock()
    client.pool_manager = mock_session

    class FakeContent:
        async def iter_chunks(self):
            yield (b'{"foo":"bar"}\n{"hello":"world"}', None)

    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.reason = "OK"
    mock_response.data = None
    mock_response.content = FakeContent()

    mock_context_manager = AsyncMock()
    mock_context_manager.__aenter__.return_value = mock_response
    mock_context_manager.__aexit__.return_value = None

    mock_session.request.return_value = mock_context_manager

    client.handle_response_exception = AsyncMock()
    client.close = AsyncMock()

    results = []
    async for item in client.stream("GET", "http://example.com"):
        results.append(item)

    assert results == [{"foo": "bar"}, {"hello": "world"}]

    client.handle_response_exception.assert_awaited_once()
    mock_response.release.assert_called_once()


@pytest.mark.asyncio
async def test_stream_exception_in_chunks():
    mock_config = MagicMock()
    mock_config.ssl_ca_cert = None
    mock_config.cert_file = None
    mock_config.key_file = None
    mock_config.verify_ssl = True
    mock_config.connection_pool_maxsize = 4
    mock_config.proxy = None
    mock_config.proxy_headers = None
    mock_config.timeout_millisec = 5000

    client = RESTClientObject(configuration=mock_config)
    mock_session = MagicMock()
    client.pool_manager = mock_session

    class FakeContent:
        async def iter_chunks(self):
            if True:  # This ensures the coroutine is actually created and awaited
                raise ValueError("Boom!")
            yield (b"", None)  # This line is never reached

    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.reason = "OK"
    mock_response.data = None
    mock_response.content = FakeContent()

    mock_context_manager = AsyncMock()
    mock_context_manager.__aenter__.return_value = mock_response
    mock_context_manager.__aexit__.return_value = None

    mock_session.request.return_value = mock_context_manager

    client.handle_response_exception = AsyncMock()
    client.close = AsyncMock()

    results = []
    try:
        async for item in client.stream("GET", "http://example.com"):
            results.append(item)
    except ValueError:
        pass

    assert results == []
    client.handle_response_exception.assert_awaited_once()
    mock_response.release.assert_called_once()


@pytest.mark.asyncio
async def test_stream_partial_chunks():
    mock_config = MagicMock()
    mock_config.ssl_ca_cert = None
    mock_config.cert_file = None
    mock_config.key_file = None
    mock_config.verify_ssl = True
    mock_config.connection_pool_maxsize = 4
    mock_config.proxy = None
    mock_config.proxy_headers = None
    mock_config.timeout_millisec = 5000

    client = RESTClientObject(configuration=mock_config)
    mock_session = MagicMock()
    client.pool_manager = mock_session

    class FakeContent:
        async def iter_chunks(self):
            yield (b'{"foo":"b', None)
            yield (b'ar"}\n{"hello":"world"}', None)

    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.reason = "OK"
    mock_response.data = None
    mock_response.content = FakeContent()

    mock_context_manager = AsyncMock()
    mock_context_manager.__aenter__.return_value = mock_response
    mock_context_manager.__aexit__.return_value = None

    mock_session.request.return_value = mock_context_manager

    client.handle_response_exception = AsyncMock()
    client.close = AsyncMock()

    results = []
    async for item in client.stream("GET", "http://example.com"):
        results.append(item)

    assert results == [{"foo": "bar"}, {"hello": "world"}]

    client.handle_response_exception.assert_awaited_once()
    mock_response.release.assert_called_once()
