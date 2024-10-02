import time
import urllib
from typing import NamedTuple

from aiohttp import ClientResponse
from urllib3 import HTTPResponse

from openfga_sdk.credentials import Credentials
from openfga_sdk.rest import RESTResponse


class TelemetryAttribute(NamedTuple):
    name: str
    format: str = None


class TelemetryAttributes:
    fga_client_request_client_id: TelemetryAttribute = TelemetryAttribute(
        name="fga-client.request.client_id",
        format="string",
    )
    fga_client_request_method: TelemetryAttribute = TelemetryAttribute(
        name="fga-client.request.method",
        format="string",
    )
    fga_client_request_model_id: TelemetryAttribute = TelemetryAttribute(
        name="fga-client.request.model_id",
        format="string",
    )
    fga_client_request_store_id: TelemetryAttribute = TelemetryAttribute(
        name="fga-client.request.store_id",
        format="string",
    )
    fga_client_response_model_id: TelemetryAttribute = TelemetryAttribute(
        name="fga-client.response.model_id",
        format="string",
    )
    fga_client_user: TelemetryAttribute = TelemetryAttribute(
        name="fga-client.user",
        format="string",
    )
    http_client_request_duration: TelemetryAttribute = TelemetryAttribute(
        name="http.client.request.duration",
        format="int",
    )
    http_host: TelemetryAttribute = TelemetryAttribute(
        name="http.host",
        format="string",
    )
    http_request_method: TelemetryAttribute = TelemetryAttribute(
        name="http.request.method",
        format="string",
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
        format="string",
    )
    url_full: TelemetryAttribute = TelemetryAttribute(
        name="url.full",
        format="string",
    )
    user_agent_original: TelemetryAttribute = TelemetryAttribute(
        name="user_agent.original",
        format="string",
    )

    def prepare(
        self,
        attributes: dict[TelemetryAttribute | str, str | int] | None,
        filter: list[TelemetryAttribute | str] | None = None,
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
                    attributeInstance = getattr(self, attributeTranslated, None)

                    if attributeInstance is None:
                        raise ValueError("Invalid attribute specified: %s" % attribute)

                    attribute = attributeInstance

                if not isinstance(attribute, TelemetryAttribute):
                    raise ValueError(
                        "Invalid attribute specified: %s" % type(attribute)
                    )

                if (
                    filter is not None
                    and attribute.name not in filter
                    and attribute not in filter
                ):
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

                response[attribute.name] = value
                continue

        return response

    def fromRequest(
        self,
        user_agent: str = None,
        fga_method: str = None,
        http_method: str = None,
        url: str = None,
        resend_count: int = None,
        start: float = None,
        credentials: Credentials = None,
        attributes: dict[TelemetryAttribute | str, str | int] = None,
    ) -> dict[TelemetryAttribute | str, str | int]:
        if attributes is None:
            attributes = {}

        if fga_method is not None:
            attributes[self.fga_client_request_method.name] = fga_method

        if user_agent is not None:
            attributes[self.user_agent_original.name] = user_agent

        if http_method is not None:
            attributes[self.http_request_method.name] = http_method

        if url is not None:
            attributes[self.http_host.name] = urllib.parse.urlparse(url).hostname
            attributes[self.url_scheme.name] = urllib.parse.urlparse(url).scheme
            attributes[self.url_full.name] = url

        if start is not None and start > 0:
            attributes[self.http_client_request_duration.name] = int(
                (time.time() - start) * 1000
            )

        if resend_count is not None:
            attributes[self.http_request_resend_count.name] = resend_count

        if credentials is not None:
            if credentials.method == "client_credentials":
                attributes[self.fga_client_request_client_id.name] = (
                    credentials.configuration.client_id
                )

        return attributes

    def fromResponse(
        self,
        response: HTTPResponse | RESTResponse | ClientResponse = None,
        credentials: Credentials = None,
        attributes: dict[TelemetryAttribute | str, str | int] = None,
    ) -> dict[TelemetryAttribute | str, str | int]:
        response_model_id = None
        response_query_duration = None

        if attributes is None:
            attributes = {}

        if response is not None:
            if self.instanceHasAttribute(response, "status"):
                attributes[self.http_response_status_code.name] = int(response.status)

            if self.instanceHasCallable(response, "getheader"):
                response_model_id = response.getheader("openfga-authorization-model-id")
                response_query_duration = response.getheader("fga-query-duration-ms")

            if self.instanceHasCallable(response, "headers"):
                response_model_id = response.headers.get(
                    "openfga-authorization-model-id"
                )
                response_query_duration = response.headers.get("fga-query-duration-ms")

            if response_model_id is not None:
                attributes[self.fga_client_response_model_id.name] = response_model_id

            if response_query_duration is not None:
                attributes[self.http_server_request_duration.name] = (
                    response_query_duration
                )

            if isinstance(credentials, Credentials):
                if credentials.method == "client_credentials":
                    attributes[self.fga_client_request_client_id.name] = (
                        credentials.configuration.client_id
                    )

        return attributes

    def instanceHasAttribute(self, instance: object, attributeName: str) -> bool:
        return hasattr(instance, attributeName)

    def instanceHasCallable(self, instance: object, callableName: str) -> bool:
        instanceCallable = getattr(instance, callableName, None)

        if instanceCallable is None:
            return False

        return callable(instanceCallable)
