from typing import NamedTuple

import opentelemetry.semconv.attributes.http_attributes as SEMATTRS_HTTP
from aiohttp import ClientResponse, RequestInfo
from urllib3 import HTTPResponse

from openfga_sdk.credentials import CredentialConfiguration, Credentials
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
    response_model_id: TelemetryAttribute = TelemetryAttribute(
        name="fga-client.response.model_id",
    )
    user: TelemetryAttribute = TelemetryAttribute(
        name="fga-client.user",
    )

    def fromResponse(
        self,
        response: HTTPResponse | RESTResponse | ClientResponse = None,
        credentials: Credentials = None,
    ):
        attributes: dict[str, str | int] = {}

        if response:
            # request = None

            # if isinstance(response, ClientResponse) and response._request_info:
            #     request = response._request_info
            # elif isinstance(response, RESTResponse) and response.aiohttp_response:
            #     request = response.aiohttp_response

            # if request and request.method:
            #     attributes[SEMATTRS_HTTP.HTTP_REQUEST_METHOD] = str(request.method)

            if response.status:
                attributes[SEMATTRS_HTTP.HTTP_RESPONSE_STATUS_CODE] = int(
                    response.status
                )

            response_model_id = response.getheader("openfga-authorization-model-id")

            if response_model_id is not None:
                attributes[self.response_model_id.name] = response_model_id

        if isinstance(credentials, Credentials):
            if credentials.method == "client_credentials":
                attributes[self.request_client_id.name] = (
                    credentials.configuration.client_id
                )

        return attributes
