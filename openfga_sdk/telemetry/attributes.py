from typing import NamedTuple

from aiohttp import ClientResponse
from urllib3 import HTTPResponse

from openfga_sdk.credentials import Credentials
from openfga_sdk.rest import RESTResponse


class TelemetryAttribute(NamedTuple):
    name: str


class TelemetryAttributes:
    request_model_id: TelemetryAttribute = TelemetryAttribute(
        name="fga-client.request.model_id",
    )
    request_method: TelemetryAttribute = TelemetryAttribute(
        name="fga-client.request.method",
    )
    request_store_id: TelemetryAttribute = TelemetryAttribute(
        name="fga-client.request.store_id",
    )
    request_client_id: TelemetryAttribute = TelemetryAttribute(
        name="fga-client.request.client_id",
    )
    request_retries: TelemetryAttribute = TelemetryAttribute(
        name="fga-client.request.retries",
    )
    response_model_id: TelemetryAttribute = TelemetryAttribute(
        name="fga-client.response.model_id",
    )
    client_user: TelemetryAttribute = TelemetryAttribute(
        name="fga-client.user",
    )
    http_host: TelemetryAttribute = TelemetryAttribute(
        name="http.host",
    )
    http_method: TelemetryAttribute = TelemetryAttribute(
        name="http.method",
    )
    http_status_code: TelemetryAttribute = TelemetryAttribute(
        name="http.status_code",
    )

    def prepare(
        self, attributes: dict[TelemetryAttribute | str, str | int] | None
    ) -> dict:
        response = {}

        if attributes is not None:
            for attribute, value in attributes.items():
                if isinstance(attribute, TelemetryAttribute):
                    response[attribute.name] = value
                else:
                    response[attribute] = value

        return dict(sorted(response.items()))

    def fromResponse(
        self,
        response: HTTPResponse | RESTResponse | ClientResponse = None,
        credentials: Credentials = None,
    ):
        attributes: dict[TelemetryAttribute | str, str | int] = {}

        if response:
            if response.status:
                attributes[self.http_status_code] = int(response.status)

            response_model_id = response.getheader("openfga-authorization-model-id")

            if response_model_id is not None:
                attributes[self.response_model_id.name] = response_model_id

        if isinstance(credentials, Credentials):
            if credentials.method == "client_credentials":
                attributes[self.request_client_id.name] = (
                    credentials.configuration.client_id
                )

        return attributes
