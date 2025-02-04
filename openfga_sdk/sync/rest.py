"""
Python SDK for OpenFGA

API version: 1.x
Website: https://openfga.dev
Documentation: https://openfga.dev/docs
Support: https://openfga.dev/community
License: [Apache-2.0](https://github.com/openfga/python-sdk/blob/main/LICENSE)

NOTE: This file was auto generated by OpenAPI Generator (https://openapi-generator.tech). DO NOT EDIT.
"""

from dataclasses import dataclass
import json
import logging
import ssl

from typing import Any

import urllib3

from openfga_sdk.common.rest import RestClientBase
from openfga_sdk.protocols import (
    ConfigurationProtocol,
    RestClientRequestProtocol,
    RestClientResponseProtocol,
)


logger = logging.getLogger(__name__)


@dataclass
class RestClientResponse(RestClientResponseProtocol):
    response: urllib3.BaseHTTPResponse | None = None
    data: bytes | None = None
    status: int | None = None
    reason: str | None = None

    @property
    def headers(self) -> dict[str, str]:
        return dict(self.response.headers)


class RestClient(RestClientBase):
    _pool_manager: urllib3.ProxyManager | urllib3.PoolManager | None = None

    def __init__(
        self,
        configuration: ConfigurationProtocol,
        pool_size: int | None = None,
        pool_size_max: int | None = None,
        timeout: int | None = None,
        debug: bool | None = None,
    ) -> None:
        self._configuration = configuration
        self._pool_size = pool_size
        self._pool_size_max = pool_size_max
        self._timeout = timeout
        self._debug = debug

    @property
    def pool_manager(self) -> urllib3.ProxyManager | urllib3.PoolManager:
        """
        Returns the underlying urllib3.PoolManager or urllib3.ProxyManager object.
        """
        if self._pool_manager is None:
            pool_configuration = {
                "num_pools": self._pool_size
                or self._configuration.connection_pool_size,
                "maxsize": self._pool_size_max,
                "timeout": self._timeout,
                "cert_reqs": (
                    ssl.CERT_REQUIRED
                    if self._configuration.verify_ssl
                    else ssl.CERT_NONE
                ),
                "ca_certs": self._configuration.ssl_ca_cert,
                "cert_file": self._configuration.cert_file,
                "key_file": self._configuration.key_file,
                "ssl_context": self.ssl_context,
            }

            if self._configuration.proxy:
                self._pool_manager = urllib3.ProxyManager(
                    **pool_configuration,
                )
            else:
                self._pool_manager = urllib3.PoolManager(**pool_configuration)

        return self._pool_manager

    @pool_manager.setter
    def pool_manager(self, value: urllib3.ProxyManager | urllib3.PoolManager) -> None:
        self._pool_manager = value

    def close(self) -> None:
        self.pool_manager.clear()

    def stream(
        self,
        request: RestClientRequestProtocol,
        timeout: float | None = None,
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

        # Initialize buffers for data chunks
        buffer = bytearray()
        leftover = b""

        # Send request, collect response handler
        response = self.pool_manager.request(
            method=request.method,
            url=request.url,
            data=request.body,
            headers=request.headers,
            params=request.fields,
            proxy=self._configuration.proxy,
            proxy_headers=self._configuration.proxy_headers,
        )

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
            self._handle_response_exception(response)

            # Release the response object (required!)
            response.release_conn()

        # Release the connection back to the pool
        self.close()

    def request(
        self,
        request: RestClientRequestProtocol,
        timeout: int | None = None,
    ) -> RestClientResponseProtocol:
        """
        Configure and send a request.

        :param method: The HTTP method.
        :param url: The endpoint URL.
        :param query_params: Query parameters to be appended to the URL.
        :param headers: Optional request headers.
        :param body: A request body for JSON or other content types.
        :param post_params: form/multipart parameters for the request.
        :param timeout: An optional request timeout in seconds.
        """

        # Send request and collect response
        response: urllib3.BaseHTTPResponse = self.pool_manager.request(
            method=request.method,
            url=request.url,
            data=request.body,
            headers=request.headers,
            params=request.fields,
            proxy=self._configuration.proxy,
            proxy_headers=self._configuration.proxy_headers,
        )

        # Transform response JSON data into RESTResponse object
        wrapped_response = RestClientResponse(
            data=response.data.decode("utf-8"),
            status=response.status,
            reason=response.reason,
            response=response,
        )

        self._log_response(wrapped_response)
        self._handle_response_exception(wrapped_response)

        return wrapped_response
