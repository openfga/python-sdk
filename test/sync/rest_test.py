import json
import ssl

from unittest.mock import MagicMock, patch

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
from openfga_sdk.sync.rest import RESTClientObject, RESTResponse


def test_restresponse_init():
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


def test_build_request_json_body():
    mock_config = MagicMock(
        spec=[
            "verify_ssl",
            "ssl_ca_cert",
            "cert_file",
            "key_file",
            "assert_hostname",
            "retries",
            "socket_options",
            "connection_pool_maxsize",
            "timeout_millisec",
            "proxy",
            "proxy_headers",
        ]
    )
    mock_config.ssl_ca_cert = None
    mock_config.cert_file = None
    mock_config.key_file = None
    mock_config.verify_ssl = True
    mock_config.connection_pool_maxsize = 4
    mock_config.timeout_millisec = 5000
    mock_config.proxy = None
    mock_config.proxy_headers = None

    client = RESTClientObject(configuration=mock_config)
    req_args = client.build_request(
        method="POST",
        url="http://example.com/test",
        body={"foo": "bar"},
        headers={"Content-Type": "application/json"},
    )

    assert req_args["method"] == "POST"
    assert req_args["url"] == "http://example.com/test"
    assert req_args["headers"]["Content-Type"] == "application/json"
    assert json.loads(req_args["body"]) == {"foo": "bar"}


def test_build_request_multipart():
    mock_config = MagicMock(
        spec=[
            "verify_ssl",
            "ssl_ca_cert",
            "cert_file",
            "key_file",
            "assert_hostname",
            "retries",
            "socket_options",
            "connection_pool_maxsize",
            "timeout_millisec",
            "proxy",
            "proxy_headers",
        ]
    )
    mock_config.ssl_ca_cert = None
    mock_config.cert_file = None
    mock_config.key_file = None
    mock_config.verify_ssl = True
    mock_config.connection_pool_maxsize = 4
    mock_config.timeout_millisec = 5000
    mock_config.proxy = None
    mock_config.proxy_headers = None

    client = RESTClientObject(configuration=mock_config)
    req_args = client.build_request(
        method="POST",
        url="http://example.com/upload",
        post_params={"file": ("filename.txt", b"contents", "text/plain")},
        headers={"Content-Type": "multipart/form-data"},
    )

    assert req_args["method"] == "POST"
    assert req_args["url"] == "http://example.com/upload"
    assert "Content-Type" not in req_args["headers"]
    assert req_args["encode_multipart"] is True
    assert req_args["fields"] == {"file": ("filename.txt", b"contents", "text/plain")}


def test_build_request_timeout():
    mock_config = MagicMock(
        spec=[
            "verify_ssl",
            "ssl_ca_cert",
            "cert_file",
            "key_file",
            "assert_hostname",
            "retries",
            "socket_options",
            "connection_pool_maxsize",
            "timeout_millisec",
            "proxy",
            "proxy_headers",
        ]
    )
    mock_config.ssl_ca_cert = None
    mock_config.cert_file = None
    mock_config.key_file = None
    mock_config.verify_ssl = True
    mock_config.connection_pool_maxsize = 4
    mock_config.timeout_millisec = 5000
    mock_config.proxy = None
    mock_config.proxy_headers = None

    client = RESTClientObject(configuration=mock_config)
    req_args = client.build_request(
        method="GET",
        url="http://example.com",
        _request_timeout=10.0,
    )

    # We'll just confirm that the "timeout" object was set to 10.0
    # A deeper check might be verifying urllib3.Timeout, but this suffices.
    assert req_args["timeout"].total == 10.0


def test_handle_response_exception_success():
    mock_config = MagicMock(
        spec=[
            "verify_ssl",
            "ssl_ca_cert",
            "cert_file",
            "key_file",
            "assert_hostname",
            "retries",
            "socket_options",
            "connection_pool_maxsize",
            "timeout_millisec",
            "proxy",
            "proxy_headers",
        ]
    )
    mock_config.ssl_ca_cert = None
    mock_config.cert_file = None
    mock_config.key_file = None
    mock_config.verify_ssl = True
    mock_config.connection_pool_maxsize = 4
    mock_config.timeout_millisec = 5000
    mock_config.proxy = None
    mock_config.proxy_headers = None

    client = RESTClientObject(configuration=mock_config)
    mock_response = MagicMock()
    mock_response.status = 200

    client.handle_response_exception(mock_response)  # no exception


@pytest.mark.parametrize(
    "status,exc",
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
def test_handle_response_exception_error(status, exc):
    mock_config = MagicMock(
        spec=[
            "verify_ssl",
            "ssl_ca_cert",
            "cert_file",
            "key_file",
            "assert_hostname",
            "retries",
            "socket_options",
            "connection_pool_maxsize",
            "timeout_millisec",
            "proxy",
            "proxy_headers",
        ]
    )
    mock_config.ssl_ca_cert = None
    mock_config.cert_file = None
    mock_config.key_file = None
    mock_config.verify_ssl = True
    mock_config.connection_pool_maxsize = 4
    mock_config.timeout_millisec = 5000
    mock_config.proxy = None
    mock_config.proxy_headers = None

    client = RESTClientObject(configuration=mock_config)
    mock_response = MagicMock()
    mock_response.status = status

    with pytest.raises(exc):
        client.handle_response_exception(mock_response)


def test_close():
    mock_config = MagicMock(
        spec=[
            "verify_ssl",
            "ssl_ca_cert",
            "cert_file",
            "key_file",
            "assert_hostname",
            "retries",
            "socket_options",
            "connection_pool_maxsize",
            "timeout_millisec",
            "proxy",
            "proxy_headers",
        ]
    )
    mock_config.ssl_ca_cert = None
    mock_config.cert_file = None
    mock_config.key_file = None
    mock_config.verify_ssl = True
    mock_config.connection_pool_maxsize = 4
    mock_config.timeout_millisec = 5000
    mock_config.proxy = None
    mock_config.proxy_headers = None

    client = RESTClientObject(configuration=mock_config)
    mock_pool_manager = MagicMock()
    client.pool_manager = mock_pool_manager

    client.close()

    mock_pool_manager.clear.assert_called_once()


def test_request_preload_content():
    mock_config = MagicMock(
        spec=[
            "verify_ssl",
            "ssl_ca_cert",
            "cert_file",
            "key_file",
            "assert_hostname",
            "retries",
            "socket_options",
            "connection_pool_maxsize",
            "timeout_millisec",
            "proxy",
            "proxy_headers",
        ]
    )
    mock_config.ssl_ca_cert = None
    mock_config.cert_file = None
    mock_config.key_file = None
    mock_config.verify_ssl = True
    mock_config.connection_pool_maxsize = 4
    mock_config.timeout_millisec = 5000
    mock_config.proxy = None
    mock_config.proxy_headers = None

    client = RESTClientObject(configuration=mock_config)
    mock_pool_manager = MagicMock()
    client.pool_manager = mock_pool_manager

    mock_raw_response = MagicMock()
    mock_raw_response.status = 200
    mock_raw_response.reason = "OK"
    mock_raw_response.data = b'{"some":"data"}'

    mock_pool_manager.request.return_value = mock_raw_response

    resp = client.request(method="GET", url="http://example.com", _preload_content=True)

    mock_pool_manager.request.assert_called_once()
    assert isinstance(resp, RESTResponse)
    assert resp.status == 200
    assert resp.data == b'{"some":"data"}'


def test_request_no_preload_content():
    mock_config = MagicMock(
        spec=[
            "verify_ssl",
            "ssl_ca_cert",
            "cert_file",
            "key_file",
            "assert_hostname",
            "retries",
            "socket_options",
            "connection_pool_maxsize",
            "timeout_millisec",
            "proxy",
            "proxy_headers",
        ]
    )
    mock_config.ssl_ca_cert = None
    mock_config.cert_file = None
    mock_config.key_file = None
    mock_config.verify_ssl = True
    mock_config.connection_pool_maxsize = 4
    mock_config.timeout_millisec = 5000
    mock_config.proxy = None
    mock_config.proxy_headers = None

    client = RESTClientObject(configuration=mock_config)
    mock_pool_manager = MagicMock()
    client.pool_manager = mock_pool_manager

    mock_raw_response = MagicMock()
    mock_raw_response.status = 200
    mock_raw_response.reason = "OK"
    mock_raw_response.data = b"unused"

    mock_pool_manager.request.return_value = mock_raw_response

    resp = client.request(
        method="GET", url="http://example.com", _preload_content=False
    )

    mock_pool_manager.request.assert_called_once()
    # We expect the raw HTTPResponse
    assert resp == mock_raw_response
    assert resp.status == 200


def test_stream_happy_path():
    mock_config = MagicMock(
        spec=[
            "verify_ssl",
            "ssl_ca_cert",
            "cert_file",
            "key_file",
            "assert_hostname",
            "retries",
            "socket_options",
            "connection_pool_maxsize",
            "timeout_millisec",
            "proxy",
            "proxy_headers",
        ]
    )
    mock_config.ssl_ca_cert = None
    mock_config.cert_file = None
    mock_config.key_file = None
    mock_config.verify_ssl = True
    mock_config.connection_pool_maxsize = 4
    mock_config.timeout_millisec = 5000
    mock_config.proxy = None
    mock_config.proxy_headers = None

    client = RESTClientObject(configuration=mock_config)
    mock_pool_manager = MagicMock()
    client.pool_manager = mock_pool_manager

    class FakeHTTPResponse:
        def __init__(self):
            self.status = 200
            self.reason = "OK"

        def stream(self, chunk_size):
            # Single chunk with two JSON lines
            yield b'{"foo":"bar"}\n{"hello":"world"}'

        def release_conn(self):
            pass

    mock_response = FakeHTTPResponse()
    mock_pool_manager.request.return_value = mock_response

    results = list(client.stream("GET", "http://example.com"))

    assert results == [{"foo": "bar"}, {"hello": "world"}]
    mock_pool_manager.request.assert_called_once()


def test_stream_partial_chunks():
    mock_config = MagicMock(
        spec=[
            "verify_ssl",
            "ssl_ca_cert",
            "cert_file",
            "key_file",
            "assert_hostname",
            "retries",
            "socket_options",
            "connection_pool_maxsize",
            "timeout_millisec",
            "proxy",
            "proxy_headers",
        ]
    )
    mock_config.ssl_ca_cert = None
    mock_config.cert_file = None
    mock_config.key_file = None
    mock_config.verify_ssl = True
    mock_config.connection_pool_maxsize = 4
    mock_config.timeout_millisec = 5000
    mock_config.proxy = None
    mock_config.proxy_headers = None

    client = RESTClientObject(configuration=mock_config)
    mock_pool_manager = MagicMock()
    client.pool_manager = mock_pool_manager

    class FakeHTTPResponse:
        def __init__(self):
            self.status = 200
            self.reason = "OK"

        def stream(self, chunk_size):
            # Two partial chunks that form "foo":"bar" plus a second object
            yield b'{"foo":"b'
            yield b'ar"}\n{"hello":"world"}'

        def release_conn(self):
            pass

    mock_response = FakeHTTPResponse()
    mock_pool_manager.request.return_value = mock_response

    results = list(client.stream("GET", "http://example.com"))

    assert results == [{"foo": "bar"}, {"hello": "world"}]
    mock_pool_manager.request.assert_called_once()


def test_stream_exception_in_chunks():
    mock_config = MagicMock(
        spec=[
            "verify_ssl",
            "ssl_ca_cert",
            "cert_file",
            "key_file",
            "assert_hostname",
            "retries",
            "socket_options",
            "connection_pool_maxsize",
            "timeout_millisec",
            "proxy",
            "proxy_headers",
        ]
    )
    mock_config.ssl_ca_cert = None
    mock_config.cert_file = None
    mock_config.key_file = None
    mock_config.verify_ssl = True
    mock_config.connection_pool_maxsize = 4
    mock_config.timeout_millisec = 5000
    mock_config.proxy = None
    mock_config.proxy_headers = None

    client = RESTClientObject(configuration=mock_config)
    mock_pool_manager = MagicMock()
    client.pool_manager = mock_pool_manager

    class FakeHTTPResponse:
        def __init__(self):
            self.status = 200
            self.reason = "OK"

        def stream(self, chunk_size):
            # Raise an exception while streaming
            raise ValueError("Boom!")

        def release_conn(self):
            pass

    mock_response = FakeHTTPResponse()
    mock_pool_manager.request.return_value = mock_response

    results = list(client.stream("GET", "http://example.com"))
    # Exception is logged, we yield nothing
    assert results == []
    mock_pool_manager.request.assert_called_once()


# Tests for SSL Context Reuse (fix for OpenSSL 3.0+ performance issues)
@patch("ssl.create_default_context")
@patch("urllib3.PoolManager")
def test_ssl_context_created_with_ca_cert(mock_pool_manager, mock_create_context):
    """Test that SSL context is created with CA certificate file."""
    mock_ssl_context = MagicMock()
    mock_create_context.return_value = mock_ssl_context

    mock_config = MagicMock()
    mock_config.ssl_ca_cert = "/path/to/ca.pem"
    mock_config.cert_file = None
    mock_config.key_file = None
    mock_config.verify_ssl = True
    mock_config.connection_pool_maxsize = 4
    mock_config.timeout_millisec = 5000
    mock_config.proxy = None

    RESTClientObject(configuration=mock_config)

    # Verify SSL context was created with CA file
    mock_create_context.assert_called_once_with(cafile="/path/to/ca.pem")

    # Verify SSL context was passed to PoolManager
    mock_pool_manager.assert_called_once()
    call_kwargs = mock_pool_manager.call_args[1]
    assert call_kwargs["ssl_context"] == mock_ssl_context


@patch("ssl.create_default_context")
@patch("urllib3.PoolManager")
def test_ssl_context_loads_client_certificate(mock_pool_manager, mock_create_context):
    """Test that SSL context loads client certificate and key when provided."""
    mock_ssl_context = MagicMock()
    mock_create_context.return_value = mock_ssl_context

    mock_config = MagicMock()
    mock_config.ssl_ca_cert = None
    mock_config.cert_file = "/path/to/client.pem"
    mock_config.key_file = "/path/to/client.key"
    mock_config.verify_ssl = True
    mock_config.connection_pool_maxsize = 4
    mock_config.timeout_millisec = 5000
    mock_config.proxy = None

    RESTClientObject(configuration=mock_config)

    # Verify SSL context was created
    mock_create_context.assert_called_once_with(cafile=None)

    # Verify client certificate was loaded
    mock_ssl_context.load_cert_chain.assert_called_once_with(
        "/path/to/client.pem", keyfile="/path/to/client.key"
    )

    # Verify SSL context was passed to PoolManager
    mock_pool_manager.assert_called_once()
    call_kwargs = mock_pool_manager.call_args[1]
    assert call_kwargs["ssl_context"] == mock_ssl_context


@patch("ssl.create_default_context")
@patch("urllib3.PoolManager")
def test_ssl_context_disables_verification_when_verify_ssl_false(
    mock_pool_manager, mock_create_context
):
    """Test that SSL context disables verification when verify_ssl=False."""
    mock_ssl_context = MagicMock()
    mock_create_context.return_value = mock_ssl_context

    mock_config = MagicMock()
    mock_config.ssl_ca_cert = None
    mock_config.cert_file = None
    mock_config.key_file = None
    mock_config.verify_ssl = False
    mock_config.connection_pool_maxsize = 4
    mock_config.timeout_millisec = 5000
    mock_config.proxy = None

    RESTClientObject(configuration=mock_config)

    # Verify SSL context was created
    mock_create_context.assert_called_once_with(cafile=None)

    # Verify SSL verification was disabled
    assert mock_ssl_context.check_hostname is False
    assert mock_ssl_context.verify_mode == ssl.CERT_NONE

    # Verify SSL context was passed to PoolManager
    mock_pool_manager.assert_called_once()
    call_kwargs = mock_pool_manager.call_args[1]
    assert call_kwargs["ssl_context"] == mock_ssl_context


@patch("ssl.create_default_context")
@patch("urllib3.ProxyManager")
def test_ssl_context_used_with_proxy_manager(mock_proxy_manager, mock_create_context):
    """Test that SSL context is passed to ProxyManager when proxy is configured."""
    mock_ssl_context = MagicMock()
    mock_create_context.return_value = mock_ssl_context

    mock_config = MagicMock()
    mock_config.ssl_ca_cert = "/path/to/ca.pem"
    mock_config.cert_file = "/path/to/client.pem"
    mock_config.key_file = "/path/to/client.key"
    mock_config.verify_ssl = True
    mock_config.connection_pool_maxsize = 4
    mock_config.timeout_millisec = 5000
    mock_config.proxy = "http://proxy:8080"
    mock_config.proxy_headers = {"Proxy-Auth": "token"}

    RESTClientObject(configuration=mock_config)

    # Verify SSL context was created with CA file
    mock_create_context.assert_called_once_with(cafile="/path/to/ca.pem")

    # Verify client certificate was loaded
    mock_ssl_context.load_cert_chain.assert_called_once_with(
        "/path/to/client.pem", keyfile="/path/to/client.key"
    )

    # Verify SSL context was passed to ProxyManager
    mock_proxy_manager.assert_called_once()
    call_kwargs = mock_proxy_manager.call_args[1]
    assert call_kwargs["ssl_context"] == mock_ssl_context
    assert call_kwargs["proxy_url"] == "http://proxy:8080"
    assert call_kwargs["proxy_headers"] == {"Proxy-Auth": "token"}


@patch("ssl.create_default_context")
@patch("urllib3.PoolManager")
def test_ssl_context_reuse_performance_optimization(
    mock_pool_manager, mock_create_context
):
    """Test that SSL context creation is called only once per client instance."""
    mock_ssl_context = MagicMock()
    mock_create_context.return_value = mock_ssl_context

    mock_config = MagicMock()
    mock_config.ssl_ca_cert = "/path/to/ca.pem"
    mock_config.cert_file = None
    mock_config.key_file = None
    mock_config.verify_ssl = True
    mock_config.connection_pool_maxsize = 4
    mock_config.timeout_millisec = 5000
    mock_config.proxy = None

    # Create client instance
    client = RESTClientObject(configuration=mock_config)

    # Verify SSL context was created exactly once
    mock_create_context.assert_called_once_with(cafile="/path/to/ca.pem")

    # Verify the same SSL context instance is reused
    mock_pool_manager.assert_called_once()
    call_kwargs = mock_pool_manager.call_args[1]
    assert call_kwargs["ssl_context"] is mock_ssl_context

    # Verify context was not created again during subsequent operations
    mock_create_context.reset_mock()

    # Build a request (this should not trigger SSL context creation)
    client.build_request("GET", "https://example.com")

    # SSL context should not be created again
    mock_create_context.assert_not_called()


@patch("ssl.create_default_context")
@patch("urllib3.PoolManager")
def test_ssl_context_with_all_ssl_options(mock_pool_manager, mock_create_context):
    """Test SSL context creation with all SSL configuration options set."""
    mock_ssl_context = MagicMock()
    mock_create_context.return_value = mock_ssl_context

    mock_config = MagicMock()
    mock_config.ssl_ca_cert = "/path/to/ca.pem"
    mock_config.cert_file = "/path/to/client.pem"
    mock_config.key_file = "/path/to/client.key"
    mock_config.verify_ssl = True
    mock_config.connection_pool_maxsize = 8
    mock_config.timeout_millisec = 10000
    mock_config.proxy = None

    RESTClientObject(configuration=mock_config)

    # Verify SSL context was created with CA file
    mock_create_context.assert_called_once_with(cafile="/path/to/ca.pem")

    # Verify client certificate was loaded
    mock_ssl_context.load_cert_chain.assert_called_once_with(
        "/path/to/client.pem", keyfile="/path/to/client.key"
    )

    # Verify SSL verification settings were NOT modified (verify_ssl=True)
    # check_hostname and verify_mode should remain at their default secure values
    assert (
        not hasattr(mock_ssl_context, "check_hostname")
        or mock_ssl_context.check_hostname
    )
    assert (
        not hasattr(mock_ssl_context, "verify_mode")
        or mock_ssl_context.verify_mode != ssl.CERT_NONE
    )

    # Verify SSL context was passed to PoolManager
    mock_pool_manager.assert_called_once()
    call_kwargs = mock_pool_manager.call_args[1]
    assert call_kwargs["ssl_context"] == mock_ssl_context
    assert call_kwargs["maxsize"] == 8
