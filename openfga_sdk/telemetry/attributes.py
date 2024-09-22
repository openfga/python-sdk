import time
import urllib
from typing import NamedTuple, Optional

from aiohttp import ClientResponse
from urllib3 import HTTPResponse

from openfga_sdk.credentials import Credentials
from openfga_sdk.exceptions import ApiException
from openfga_sdk.rest import RESTResponse
from openfga_sdk.telemetry.utilities import (
    doesInstanceHaveCallable,
)


class TelemetryAttribute(NamedTuple):
    name: str
    format: str = "string"


class TelemetryAttributes:
    fga_client_request_client_id: TelemetryAttribute = TelemetryAttribute(
        name="fga-client.request.client_id",
    )
    fga_client_request_method: TelemetryAttribute = TelemetryAttribute(
        name="fga-client.request.method",
    )
    fga_client_request_model_id: TelemetryAttribute = TelemetryAttribute(
        name="fga-client.request.model_id",
    )
    fga_client_request_store_id: TelemetryAttribute = TelemetryAttribute(
        name="fga-client.request.store_id",
    )
    fga_client_response_model_id: TelemetryAttribute = TelemetryAttribute(
        name="fga-client.response.model_id",
    )
    fga_client_user: TelemetryAttribute = TelemetryAttribute(
        name="fga-client.user",
    )
    http_client_request_duration: TelemetryAttribute = TelemetryAttribute(
        name="http.client.request.duration",
        format="int",
    )
    http_host: TelemetryAttribute = TelemetryAttribute(
        name="http.host",
    )
    http_request_method: TelemetryAttribute = TelemetryAttribute(
        name="http.request.method",
    )
    http_request_resend_count: TelemetryAttribute = TelemetryAttribute(
        name="http.request.resend_count",
        format="int",
    )
    http_response_status_code: TelemetryAttribute = TelemetryAttribute(
        name="http.response.status_code",
        format="int",
    )
    http_server_request_duration: TelemetryAttribute = TelemetryAttribute(
        name="http.server.request.duration",
        format="int",
    )
    url_scheme: TelemetryAttribute = TelemetryAttribute(
        name="url.scheme",
    )
    url_full: TelemetryAttribute = TelemetryAttribute(
        name="url.full",
    )
    user_agent_original: TelemetryAttribute = TelemetryAttribute(
        name="user_agent.original",
    )

    _attributes: list[TelemetryAttribute] = [
        fga_client_request_client_id,
        fga_client_request_method,
        fga_client_request_model_id,
        fga_client_request_store_id,
        fga_client_response_model_id,
        fga_client_user,
        http_client_request_duration,
        http_host,
        http_request_method,
        http_request_resend_count,
        http_response_status_code,
        http_server_request_duration,
        url_scheme,
        url_full,
        user_agent_original,
    ]

    @staticmethod
    def get(
        name: Optional[str] = None,
    ) -> list[TelemetryAttribute] | TelemetryAttribute | None:
        if name is None:
            return TelemetryAttributes._attributes

        for attribute in TelemetryAttributes._attributes:
            if attribute.name == name:
                return attribute

        return None

    @staticmethod
    def prepare(
        attributes: dict[TelemetryAttribute, str | int] | None,
        filter: list[TelemetryAttribute] | None = None,
    ) -> dict[str, str | int]:
        response = {}

        if filter is None or filter == []:
            return response

        if attributes is not None:
            for attribute, value in attributes.items():
                if value is None:
                    continue

                if isinstance(attribute, str):
                    attributeTranslated = (
                        attribute.lower().replace("-", "_").replace(".", "_")
                    )
                    attributeInstance = getattr(
                        TelemetryAttributes, attributeTranslated, None
                    )

                    if attributeInstance is None:
                        raise ValueError("Invalid attribute specified: %s" % attribute)

                    attribute = attributeInstance

                if not isinstance(attribute, TelemetryAttribute):
                    raise ValueError(
                        "Invalid attribute specified: %s" % type(attribute)
                    )

                if filter is not None and attribute not in filter:
                    continue

                if attribute.format == "string":
                    if not isinstance(value, str):
                        try:
                            value = str(value)
                        except ValueError:
                            continue

                    if value == "":
                        continue

                if attribute.format == "int":
                    if not isinstance(value, int):
                        try:
                            value = int(value)
                        except ValueError:
                            continue

                if attribute.format == "float":
                    if not isinstance(value, float):
                        try:
                            value = float(value)
                        except ValueError:
                            continue

                response[attribute.name] = value
                continue

        return response

    @staticmethod
    def fromRequest(
        user_agent: str = None,
        fga_method: str = None,
        http_method: str = None,
        url: str = None,
        resend_count: int = None,
        start: float = None,
        credentials: Credentials = None,
        attributes: dict[TelemetryAttribute, str | int] = None,
    ) -> dict[TelemetryAttribute, str | int]:
        if attributes is None:
            attributes = {}

        if (
            TelemetryAttributes.fga_client_request_method not in attributes
            and fga_method is not None
        ):
            fga_method = fga_method.rsplit("/", 1)[-1]

            if fga_method:
                attributes[TelemetryAttributes.fga_client_request_method] = (
                    fga_method.rsplit("/", 1)[-1]
                )

        if TelemetryAttributes.fga_client_request_method in attributes:
            fga_method = attributes[TelemetryAttributes.fga_client_request_method]
            fga_method = (
                fga_method.lower().replace("_", " ").title().replace(" ", "").strip()
            )

            if fga_method:
                attributes[TelemetryAttributes.fga_client_request_method] = fga_method
            else:
                del attributes[TelemetryAttributes.fga_client_request_method]

        if user_agent is not None:
            attributes[TelemetryAttributes.user_agent_original] = user_agent

        if http_method is not None:
            attributes[TelemetryAttributes.http_request_method] = http_method

        if url is not None:
            attributes[TelemetryAttributes.http_host] = urllib.parse.urlparse(
                url
            ).hostname
            attributes[TelemetryAttributes.url_scheme] = urllib.parse.urlparse(
                url
            ).scheme
            attributes[TelemetryAttributes.url_full] = url

        if start is not None and start > 0:
            attributes[TelemetryAttributes.http_client_request_duration] = int(
                (time.time() - start) * 1000
            )

        if resend_count is not None and resend_count > 0:
            attributes[TelemetryAttributes.http_request_resend_count] = resend_count

        if credentials is not None:
            if credentials.method == "client_credentials":
                attributes[TelemetryAttributes.fga_client_request_client_id] = (
                    credentials.configuration.client_id
                )

        return attributes

    @staticmethod
    def fromResponse(
        response: Optional[
            HTTPResponse | RESTResponse | ClientResponse | ApiException
        ] = None,
        credentials: Optional[Credentials] = None,
        attributes: Optional[dict[TelemetryAttribute, str | int]] = None,
    ) -> dict[TelemetryAttribute, str | int]:
        response_model_id = None
        response_query_duration = None

        if attributes is None:
            attributes = {}

        if isinstance(response, ApiException):
            if response.status is not None:
                attributes[TelemetryAttributes.http_response_status_code] = int(
                    response.status
                )

            if response.body is not None:
                response_model_id = response.body.get(
                    "openfga-authorization-model-id"
                ) or response.body.get("openfga_authorization_model_id")
                response_query_duration = response.body.get("fga-query-duration-ms")

        if response is not None:
            if hasattr(response, "status"):
                attributes[TelemetryAttributes.http_response_status_code] = int(
                    response.status
                )

            if doesInstanceHaveCallable(response, "getheader"):
                response_model_id = response.getheader("openfga-authorization-model-id")
                response_query_duration = response.getheader("fga-query-duration-ms")

            if doesInstanceHaveCallable(response, "headers"):
                response_model_id = response.headers.get(
                    "openfga-authorization-model-id"
                )
                response_query_duration = response.headers.get("fga-query-duration-ms")

        if response_model_id is not None:
            attributes[TelemetryAttributes.fga_client_response_model_id] = (
                response_model_id
            )

        if response_query_duration is not None:
            attributes[TelemetryAttributes.http_server_request_duration] = (
                response_query_duration
            )

        if isinstance(credentials, Credentials):
            if credentials.method == "client_credentials":
                attributes[TelemetryAttributes.fga_client_request_client_id] = (
                    credentials.configuration.client_id
                )

        return attributes

    @staticmethod
    def coalesceAttributeValue(
        attribute: TelemetryAttribute,
        value: Optional[int | float] = None,
        attributes: Optional[dict[TelemetryAttribute, str | int]] = None,
    ) -> int | float | None:
        if value is None:
            if attribute in attributes:
                value = attributes[attribute]

        if value is not None:
            if attribute.format == "int":
                try:
                    value = int(value)
                except ValueError:
                    value = None

            if attribute.format == "float":
                try:
                    value = float(value)
                except ValueError:
                    value = None

            if attribute.format == "string":
                value = str(value)

        return value
