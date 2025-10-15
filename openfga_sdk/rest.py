import io
import json
import logging
import re
import ssl
import urllib

from typing import Any

import aiohttp

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
    Represents an HTTP response object in the asynchronous client.
    """

    _response: aiohttp.ClientResponse
    _data: bytes
    _status: int
    _reason: str | None

    def __init__(
        self,
        response: aiohttp.ClientResponse,
        data: bytes,
        status: int | None = None,
        reason: str | None = None,
    ) -> None:
        """
        Initializes a RESTResponse with an aiohttp.ClientResponse and corresponding data.

        :param resp: The aiohttp.ClientResponse object.
        :param data: The raw byte data read from the response.
        """
        self._response = response
        self._data = data
        self._status = status or response.status
        self._reason = reason or response.reason

    @property
    def response(self) -> aiohttp.ClientResponse:
        """
        Returns the underlying aiohttp.ClientResponse object.
        """
        return self._response

    @response.setter
    def response(self, value: aiohttp.ClientResponse) -> None:
        """
        Sets the underlying aiohttp.ClientResponse object.
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
        Returns the response headers.
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
    A client object that manages HTTP interactions.
    """

    def __init__(
        self, configuration: Any, pools_size: int = 4, maxsize: int | None = None
    ) -> None:
        """
        Creates a new RESTClientObject.

        :param configuration: A configuration object with necessary parameters.
        :param pools_size: The size of the connection pool (unused, present for compatibility).
        :param maxsize: Maximum number of connections to allow.
        """
        if maxsize is None:
            maxsize = configuration.connection_pool_maxsize

        ssl_context = ssl.create_default_context(cafile=configuration.ssl_ca_cert)
        if configuration.cert_file:
            ssl_context.load_cert_chain(
                configuration.cert_file, keyfile=configuration.key_file
            )

        if not configuration.verify_ssl:
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

        connector = aiohttp.TCPConnector(limit=maxsize, ssl=ssl_context)
        self.proxy = configuration.proxy
        self.proxy_headers = configuration.proxy_headers
        self._timeout_millisec = configuration.timeout_millisec
        self.pool_manager = aiohttp.ClientSession(connector=connector, trust_env=True)

    async def close(self) -> None:
        """
        Closes the underlying aiohttp.ClientSession.
        """
        await self.pool_manager.close()

    async def build_request(
        self,
        method: str,
        url: str,
        query_params: dict | None = None,
        headers: dict | None = None,
        body: Any | None = None,
        post_params: list[tuple[str, Any]] | None = None,
        _preload_content: bool = True,
        _request_timeout: float | None = None,
    ) -> dict:
        """
        Builds a dictionary of request arguments suitable for aiohttp.

        :param method: The HTTP method.
        :param url: The URL endpoint.
        :param query_params: Optional query parameters.
        :param headers: Optional request headers.
        :param body: The request body, if any.
        :param post_params: Form or multipart parameters, if any.
        :param _preload_content: If True, content will be loaded immediately (not used here).
        :param _request_timeout: Request timeout in seconds.
        :return: A dictionary of request arguments.
        """
        method = method.upper()
        assert method in ["GET", "HEAD", "DELETE", "POST", "PUT", "PATCH", "OPTIONS"]

        if post_params and body:
            raise ApiValueError(
                "body parameter cannot be used with post_params parameter."
            )

        post_params = post_params or []
        headers = headers or {}
        timeout = _request_timeout or (self._timeout_millisec / 1000)

        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

        args = {
            "method": method,
            "url": url,
            "timeout": timeout,
            "headers": headers,
        }

        if self.proxy:
            args["proxy"] = self.proxy
        if self.proxy_headers:
            args["proxy_headers"] = self.proxy_headers

        if query_params:
            encoded_qs = urllib.parse.urlencode(query_params)
            args["url"] = f"{url}?{encoded_qs}"

        if method in ["POST", "PUT", "PATCH", "OPTIONS", "DELETE"]:
            if re.search("json", headers["Content-Type"], re.IGNORECASE):
                if body is not None:
                    body = json.dumps(body)
                args["data"] = body
            elif headers["Content-Type"] == "application/x-www-form-urlencoded":
                args["data"] = aiohttp.FormData(post_params)
            elif headers["Content-Type"] == "multipart/form-data":
                del headers["Content-Type"]
                data = aiohttp.FormData()
                for param in post_params:
                    k, v = param
                    if isinstance(v, tuple) and len(v) == 3:
                        data.add_field(k, value=v[1], filename=v[0], content_type=v[2])
                    else:
                        data.add_field(k, v)
                args["data"] = data
            elif isinstance(body, bytes):
                args["data"] = body
            else:
                msg = (
                    "Cannot prepare a request message for provided arguments. "
                    "Please check that your arguments match declared content type."
                )
                raise ApiException(status=0, reason=msg)

        return args

    async def handle_response_exception(
        self, response: RESTResponse | aiohttp.ClientResponse
    ) -> None:
        """
        Raises exceptions if response status indicates an error.

        :param response: The response to check.
        :raises ValidationException: If status is 400.
        :raises UnauthorizedException: If status is 401.
        :raises ForbiddenException: If status is 403.
        :raises NotFoundException: If status is 404.
        :raises RateLimitExceededError: If status is 429.
        :raises ServiceException: If status is 5xx.
        :raises ApiException: For other non-2xx statuses.
        """
        if 200 <= response.status <= 299:
            return

        if isinstance(response, aiohttp.ClientResponse) and not hasattr(
            response, "data"
        ):
            # Read the body once and expose it for downstream error handlers
            response.data = await response.read()

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
        Processes a chunk of data and leftover bytes. Splits on newlines, decodes valid JSON,
        and returns leftover bytes and a list of decoded JSON objects.

        :param leftover: Any leftover bytes from previous chunks.
        :param data: The new chunk of data.
        :param buffer: The main bytearray buffer for all data.
        :return: Updated leftover bytes and a list of decoded JSON objects.
        """
        objects: list[Any] = []
        leftover += data
        lines = leftover.split(
            b"\n"
        )  # Objects are received as one-per-line, so split at newlines
        leftover = lines.pop()
        buffer.extend(data)
        for line in lines:
            try:
                decoded = json.loads(line.decode("utf-8"))
                objects.append(decoded)
            except json.JSONDecodeError as e:
                logger.warning("Skipping invalid JSON segment: %s", e)
        return leftover, objects

    async def stream(
        self,
        method: str,
        url: str,
        query_params: dict | None = None,
        headers: dict | None = None,
        body: Any | None = None,
        post_params: list[tuple[str, Any]] | None = None,
        _request_timeout: float | None = None,
    ):
        """
        Streams JSON objects from a specified endpoint, handling partial chunks
        and leftover data at the end of the stream.

        :param method: The HTTP method (GET, POST, etc.).
        :param url: The endpoint URL.
        :param query_params: Query parameters to be appended to the URL.
        :param headers: Optional headers to include in the request.
        :param body: Optional body for the request.
        :param post_params: Optional form/multipart parameters.
        :param _request_timeout: An optional request timeout in seconds.
        :yields: Parsed JSON objects as Python data structures.
        """

        # Build our request payload
        args = await self.build_request(
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
        response: aiohttp.ClientResponse | None = None

        try:
            # Send request, collect response handler
            async with self.pool_manager.request(**args) as resp:
                response = resp
                try:
                    # Iterate over streamed/chunked response data
                    async for data, _ in resp.content.iter_chunks():
                        if data:
                            # Process data chunk
                            leftover, decoded_objects = self._accumulate_json_lines(
                                leftover, data, buffer
                            )

                            # Yield any complete objects
                            for obj in decoded_objects:
                                yield obj

                except Exception as e:
                    logger.exception("Stream reading error: %s", e)

        except Exception as conn_err:
            logger.exception("Connection or request setup error: %s", conn_err)

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

            # Decode the complete/buffered data for logging purposes
            if isinstance(response, aiohttp.ClientResponse):
                logger.debug("response body: %s", buffer.decode("utf-8"))

            # Handle any HTTP errors that may have occurred
            await self.handle_response_exception(response)

            # Release the response object (required!)
            response.release()

    async def request(
        self,
        method: str,
        url: str,
        query_params: dict | None = None,
        headers: dict | None = None,
        body: Any | None = None,
        post_params: list[tuple[str, Any]] | None = None,
        _preload_content: bool = True,
        _request_timeout: float | None = None,
    ) -> RESTResponse | aiohttp.ClientResponse:
        """
        Executes a request and returns the response object.

        :param method: The HTTP method.
        :param url: The endpoint URL.
        :param query_params: Query parameters to be appended to the URL.
        :param headers: Optional request headers.
        :param body: A request body for JSON or other content types.
        :param post_params: Form/multipart parameters for the request.
        :param _preload_content: If True, the response body is read immediately.
        :param _request_timeout: An optional request timeout in seconds.
        :return: A RESTResponse if _preload_content is True, otherwise an aiohttp.ClientResponse.
        """

        # Build our request payload
        args = await self.build_request(
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
        raw_response: aiohttp.ClientResponse = await self.pool_manager.request(**args)

        # If we want to preload the response, read it
        if _preload_content:
            # Collect response data
            data = await raw_response.read()

            # Transform response JSON data into RESTResponse object
            wrapped_response = RESTResponse(raw_response, data)

            # Log the response body
            logger.debug("response body: %s", data.decode("utf-8"))

        # Handle any errors that may have occurred
        await self.handle_response_exception(raw_response)

        return wrapped_response or raw_response
