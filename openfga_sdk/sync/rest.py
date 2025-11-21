import io
import json
import logging
import re
import ssl
import urllib

from typing import Any

import urllib3

from openfga_sdk.exceptions import (
    ApiException,
    ApiValueError,
    ForbiddenException,
    NotFoundException,
    RateLimitExceededError,
    ServiceException,
    UnauthorizedException,
    ValidationException,
)


logger = logging.getLogger(__name__)


class RESTResponse(io.IOBase):
    """
    Represents an HTTP response object in the synchronous client.
    """

    _response: urllib3.HTTPResponse
    _data: bytes
    _status: int
    _reason: str | None

    def __init__(
        self,
        response: urllib3.HTTPResponse,
        data: bytes,
        status: int | None = None,
        reason: str | None = None,
    ) -> None:
        """
        Initializes a RESTResponse with a urllib3.HTTPResponse and corresponding data.

        :param resp: The urllib3.HTTPResponse object.
        :param data: The raw byte data read from the response.
        """
        self._response = response
        self._data = data
        self._status = status or response.status
        self._reason = reason or response.reason

    @property
    def response(self) -> urllib3.HTTPResponse:
        """
        Returns the underlying urllib3.HTTPResponse object.
        """
        return self._response

    @response.setter
    def response(self, value: urllib3.HTTPResponse) -> None:
        """
        Sets the underlying urllib3.HTTPResponse object.
        """
        self._response = value

    @property
    def data(self) -> bytes:
        """
        Returns the raw byte data of the response.
        """
        return self._data

    @data.setter
    def data(self, value: bytes) -> None:
        """
        Sets the raw byte data of the response.
        """
        self._data = value

    @property
    def status(self) -> int:
        """
        Returns the HTTP status code of the response.
        """
        return self._status

    @status.setter
    def status(self, value: int) -> None:
        """
        Sets the HTTP status code of the response.
        """
        self._status = value

    @property
    def reason(self) -> str | None:
        """
        Returns the HTTP reason phrase of the response.
        """
        return self._reason

    @reason.setter
    def reason(self, value: str | None) -> None:
        """
        Sets the HTTP reason phrase of the response.
        """
        self._reason = value

    def getheaders(self) -> dict[str, str]:
        """
        Returns a dictionary of the response headers.
        """
        return dict(self.response.headers)

    def getheader(self, name: str, default: str | None = None) -> str | None:
        """
        Returns a specific header value by name.

        :param name: The name of the header.
        :param default: The default value if header is not found.
        :return: The header value, or default if not present.
        """
        return self.response.headers.get(name, default)


class RESTClientObject:
    """
    A synchronous client object that manages HTTP interactions using urllib3.
    """

    def __init__(
        self,
        configuration: Any,
        pools_size: int = 4,
        maxsize: int | None = None,
    ) -> None:
        """
        Creates a new RESTClientObject using urllib3.

        :param configuration: A configuration object with necessary parameters.
        :param pools_size: The number of connection pools to use.
        :param maxsize: The maximum number of connections per pool.
        """

        # Reuse SSL context to mitigate OpenSSL 3.0+ performance issues
        # See: https://github.com/openssl/openssl/issues/17064
        ssl_context = ssl.create_default_context(cafile=configuration.ssl_ca_cert)

        if configuration.cert_file:
            ssl_context.load_cert_chain(
                configuration.cert_file, keyfile=configuration.key_file
            )

        if not configuration.verify_ssl:
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

        addition_pool_args = {}

        if (
            hasattr(configuration, "assert_hostname")
            and configuration.assert_hostname is not None
        ):
            addition_pool_args["assert_hostname"] = configuration.assert_hostname

        if hasattr(configuration, "retries") and configuration.retries is not None:
            addition_pool_args["retries"] = configuration.retries

        if (
            hasattr(configuration, "socket_options")
            and configuration.socket_options is not None
        ):
            addition_pool_args["socket_options"] = configuration.socket_options

        if maxsize is None:
            if (
                hasattr(configuration, "connection_pool_maxsize")
                and configuration.connection_pool_maxsize is not None
            ):
                maxsize = configuration.connection_pool_maxsize
            else:
                maxsize = 4

        self._timeout_millisec = configuration.timeout_millisec

        if hasattr(configuration, "proxy") and configuration.proxy is not None:
            self.pool_manager: urllib3.ProxyManager | urllib3.PoolManager = (
                urllib3.ProxyManager(
                    num_pools=pools_size,
                    maxsize=maxsize,
                    ssl_context=ssl_context,
                    proxy_url=configuration.proxy,
                    proxy_headers=configuration.proxy_headers,
                    **addition_pool_args,
                )
            )

            return

        self.pool_manager = urllib3.PoolManager(
            num_pools=pools_size,
            maxsize=maxsize,
            ssl_context=ssl_context,
            **addition_pool_args,
        )

    def close(self) -> None:
        """
        Closes all pooled connections.
        """
        self.pool_manager.clear()

    def build_request(
        self,
        method: str,
        url: str,
        query_params: dict | None = None,
        headers: dict | None = None,
        body: Any | None = None,
        post_params: dict | None = None,
        _preload_content: bool = True,
        _request_timeout: float | tuple | None = None,
    ) -> dict:
        """
        Builds a dictionary of request arguments suitable for urllib3.

        :param method: The HTTP method (GET, POST, etc.).
        :param url: The URL endpoint.
        :param query_params: Optional query parameters.
        :param headers: Optional request headers.
        :param body: The request body, if any.
        :param post_params: Form or multipart parameters, if any.
        :param _preload_content: If True, response data is read immediately (by urllib3).
        :param _request_timeout: Timeout setting, in seconds or a (connect, read) tuple.
        :return: A dictionary of request arguments for urllib3.
        """
        method = method.upper()
        assert method in ["GET", "HEAD", "DELETE", "POST", "PUT", "PATCH", "OPTIONS"]

        if post_params and body:
            raise ApiValueError(
                "body parameter cannot be used with post_params parameter."
            )

        headers = headers or {}
        post_params = post_params or {}
        timeout_val = _request_timeout or self._timeout_millisec

        if isinstance(timeout_val, float | int):
            if timeout_val > 100:
                timeout_val /= 1000
            timeout = urllib3.Timeout(total=timeout_val)
        elif isinstance(timeout_val, tuple) and len(timeout_val) == 2:
            connect_t, read_t = timeout_val
            if connect_t > 100:
                connect_t /= 1000
            if read_t > 100:
                read_t /= 1000
            timeout = urllib3.Timeout(connect=connect_t, read=read_t)
        else:
            timeout = urllib3.Timeout(total=None)  # fallback

        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

        args = {
            "method": method,
            "url": url,
            "timeout": timeout,
            "headers": headers,
            "preload_content": _preload_content,
        }

        if query_params:
            encoded_qs = urllib.parse.urlencode(query_params)
            args["url"] = f"{url}?{encoded_qs}"

        # Handle body/post_params for methods that send payloads
        if method in ["POST", "PUT", "PATCH", "OPTIONS", "DELETE"]:
            if re.search("json", headers["Content-Type"], re.IGNORECASE):
                if body is not None:
                    body = json.dumps(body)
                args["body"] = body

            elif headers["Content-Type"] == "application/x-www-form-urlencoded":
                args["fields"] = post_params
                args["encode_multipart"] = False

            elif headers["Content-Type"] == "multipart/form-data":
                del headers["Content-Type"]
                args["fields"] = post_params
                args["encode_multipart"] = True

            elif isinstance(body, str | bytes):
                args["body"] = body
            else:
                msg = (
                    "Cannot prepare a request message for provided arguments. "
                    "Please check that your arguments match declared content type."
                )
                raise ApiException(status=0, reason=msg)
        else:
            # For GET, HEAD, etc., we can pass query_params as fields if needed
            # but we've already appended them to the URL above
            pass

        return args

    def handle_response_exception(
        self, response: RESTResponse | urllib3.HTTPResponse
    ) -> None:
        """
        Raises exceptions if response status indicates an error.

        :param response: The response to check (could be RESTResponse or raw urllib3.HTTPResponse).
        """
        if 200 <= response.status <= 299:
            return

        match response.status:
            case 400:
                raise ValidationException(http_resp=response)
            case 401:
                raise UnauthorizedException(http_resp=response)
            case 403:
                raise ForbiddenException(http_resp=response)
            case 404:
                raise NotFoundException(http_resp=response)
            case 429:
                raise RateLimitExceededError(http_resp=response)
            case _ if 500 <= response.status <= 599:
                raise ServiceException(http_resp=response)
            case _:
                raise ApiException(http_resp=response)

    def _accumulate_json_lines(
        self, leftover: bytes, data: bytes, buffer: bytearray
    ) -> tuple[bytes, list[Any]]:
        """
        Processes a chunk of data plus any leftover bytes from a previous iteration.
        Splits on newlines, decodes valid JSON lines, and returns updated leftover bytes
        plus a list of decoded JSON objects.

        :param leftover: Any leftover bytes from previous chunks.
        :param data: The new chunk of data.
        :param buffer: The main bytearray buffer for all data in this request.
        :return: A tuple of (updated leftover bytes, list of decoded objects).
        """
        objects: list[Any] = []
        leftover += data
        lines = leftover.split(
            b"\n"
        )  # Objects are received as one-per-line, so split at newlines
        leftover = lines.pop()
        buffer.extend(data)

        for line in lines:
            line_str = line.decode("utf-8")
            try:
                decoded = json.loads(line_str)
                objects.append(decoded)
            except json.JSONDecodeError as e:
                logger.warning("Skipping invalid JSON segment: %s", e)

        return leftover, objects

    def stream(
        self,
        method: str,
        url: str,
        query_params: dict | None = None,
        headers: dict | None = None,
        body: Any | None = None,
        post_params: dict | None = None,
        _request_timeout: float | tuple | None = None,
    ):
        """
        Streams JSON objects from a specified endpoint, reassembling partial chunks
        and yielding one decoded object at a time.

        :param method: The HTTP method (GET, POST, etc.).
        :param url: The endpoint URL.
        :param query_params: Query parameters to be appended to the URL.
        :param headers: Optional headers to include in the request.
        :param body: Optional body for the request.
        :param post_params: Optional form/multipart parameters.
        :param _request_timeout: An optional request timeout in seconds or (connect, read) tuple.
        :yields: Parsed JSON objects as Python data structures.
        """

        # Build our request payload
        args = self.build_request(
            method,
            url,
            query_params=query_params,
            headers=headers,
            body=body,
            post_params=post_params,
            _preload_content=False,
            _request_timeout=_request_timeout,
        )

        # Initialize buffers for data chunks
        buffer = bytearray()
        leftover = b""

        # Send request, collect response handler
        response = self.pool_manager.request(**args)

        try:
            # Iterate over streamed/chunked response data
            for chunk in response.stream(1024):
                # Process data chunk
                leftover, decoded_objects = self._accumulate_json_lines(
                    leftover, chunk, buffer
                )

                # Yield any complete objects
                yield from decoded_objects

        except Exception as e:
            logger.exception("Stream error: %s", e)

        # Handle any remaining data after stream ends
        if response is not None:
            # Check for any leftover data
            if leftover:
                try:
                    # Attempt to decode and yield any remaining JSON object
                    final_str = leftover.decode("utf-8")
                    final_obj = json.loads(final_str)
                    buffer.extend(leftover)
                    yield final_obj

                except json.JSONDecodeError:
                    logger.debug("Incomplete leftover data at end of stream.")

            # Handle any HTTP errors that may have occurred
            self.handle_response_exception(response)

            # Release the response object (required!)
            response.release_conn()

    def request(
        self,
        method: str,
        url: str,
        query_params: dict | None = None,
        headers: dict | None = None,
        body: Any | None = None,
        post_params: dict | None = None,
        _preload_content: bool = True,
        _request_timeout: float | tuple | None = None,
    ) -> RESTResponse | urllib3.HTTPResponse:
        """
        Executes a request and returns the response object.

        :param method: The HTTP method.
        :param url: The endpoint URL.
        :param query_params: Query parameters to be appended to the URL.
        :param headers: Optional request headers.
        :param body: A request body for JSON or other content types.
        :param post_params: Form/multipart parameters for the request.
        :param _preload_content: If True, the response body is read immediately
                                 and wrapped in a RESTResponse. Otherwise,
                                 an un-consumed urllib3.HTTPResponse is returned.
        :param _request_timeout: Timeout in seconds or a (connect, read) tuple.
        :return: A RESTResponse if _preload_content=True, otherwise a raw HTTPResponse.
        """

        # Build our request payload
        args = self.build_request(
            method,
            url,
            query_params=query_params,
            headers=headers,
            body=body,
            post_params=post_params,
            _preload_content=_preload_content,
            _request_timeout=_request_timeout,
        )

        # Send request, collect response handler
        wrapped_response: RESTResponse | None = None
        raw_response: urllib3.HTTPResponse = self.pool_manager.request(**args)

        # If we want to preload the response, read it
        if _preload_content:
            # Collect response data and transform response (JSON) into RESTResponse object
            wrapped_response = RESTResponse(raw_response, raw_response.data)

            # Log the response body
            logger.debug("response body: %s", wrapped_response.data.decode("utf-8"))

        # Handle any errors that may have occurred
        self.handle_response_exception(raw_response)

        # Release the connection back to the pool
        self.close()

        return wrapped_response or raw_response
