import time
import urllib

from typing import Any, NamedTuple

from aiohttp import ClientResponse
from urllib3 import HTTPResponse

from openfga_sdk.credentials import Credentials
from openfga_sdk.exceptions import ApiException
from openfga_sdk.rest import RESTResponse


class TelemetryAttribute(NamedTuple):
    name: str
    format: str = "string"


class TelemetryAttributes:
    fga_client_request_batch_check_size: TelemetryAttribute = TelemetryAttribute(
        name="fga-client.request.batch_check_size", format="int"
    )
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
        fga_client_request_batch_check_size,
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
    def getAll() -> list[TelemetryAttribute]:
        return TelemetryAttributes._attributes

    @staticmethod
    def get(
        name: str | None = None,
    ) -> TelemetryAttribute | None:
        for attribute in TelemetryAttributes._attributes:
            if attribute.name == name:
                return attribute

        return None

    @staticmethod
    def prepare(
        attributes: dict[TelemetryAttribute, str | bool | int | float] | None = None,
        filter: list[TelemetryAttribute] | dict[TelemetryAttribute, bool] | None = None,
    ) -> dict[str, str | bool | int | float]:
        response: dict[str, str | bool | int | float] = {}

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
                        raise ValueError(f"Invalid attribute specified: {attribute}")

                    attribute = attributeInstance

                if not isinstance(attribute, TelemetryAttribute):
                    raise ValueError(f"Invalid attribute specified: {type(attribute)}")

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
    def fromBody(
        body: Any,
        attributes: dict[TelemetryAttribute, str | bool | int | float] | None = None,
    ):
        from openfga_sdk.models.batch_check_request import BatchCheckRequest

        if attributes is None:
            attributes = {}

        if (
            TelemetryAttributes.fga_client_request_batch_check_size not in attributes
            and isinstance(body, BatchCheckRequest)
        ):
            attributes[TelemetryAttributes.fga_client_request_batch_check_size] = len(
                body.checks
            )

        return attributes

    @staticmethod
    def fromRequest(
        user_agent: str | None = None,
        fga_method: str | None = None,
        http_method: str | None = None,
        url: str | None = None,
        resend_count: int | None = None,
        start: float | None = None,
        credentials: Credentials | None = None,
        attributes: dict[TelemetryAttribute, str | bool | int | float] | None = None,
    ) -> dict[TelemetryAttribute, str | bool | int | float]:
        _attributes: dict[TelemetryAttribute, str | bool | int | float] = {}

        if attributes is not None:
            _attributes = attributes

        if (
            TelemetryAttributes.fga_client_request_method not in _attributes
            and fga_method is not None
        ):
            fga_method = fga_method.rsplit("/", 1)[-1]

            if fga_method:
                _attributes[TelemetryAttributes.fga_client_request_method] = (
                    fga_method.rsplit("/", 1)[-1]
                )

        if TelemetryAttributes.fga_client_request_method in _attributes:
            _attr_fga_method = _attributes[
                TelemetryAttributes.fga_client_request_method
            ]

            if type(_attr_fga_method) is str:
                _attr_fga_method = (
                    _attr_fga_method.lower()
                    .replace("_", " ")
                    .title()
                    .replace(" ", "")
                    .strip()
                )

                if _attr_fga_method:
                    _attributes[TelemetryAttributes.fga_client_request_method] = (
                        _attr_fga_method
                    )
                else:
                    del _attributes[TelemetryAttributes.fga_client_request_method]

        if user_agent is not None:
            _attributes[TelemetryAttributes.user_agent_original] = user_agent

        if http_method is not None:
            _attributes[TelemetryAttributes.http_request_method] = http_method

        if url is not None:
            _hostname = urllib.parse.urlparse(url).hostname
            _scheme = urllib.parse.urlparse(url).scheme

            if type(_hostname) is str:
                _attributes[TelemetryAttributes.http_host] = _hostname

            if type(_scheme) is str:
                _attributes[TelemetryAttributes.url_scheme] = _scheme

            _attributes[TelemetryAttributes.url_full] = url

        if start is not None and start > 0:
            _attributes[TelemetryAttributes.http_client_request_duration] = int(
                (time.time() - start) * 1000
            )

        if resend_count is not None and resend_count > 0:
            _attributes[TelemetryAttributes.http_request_resend_count] = resend_count

        if credentials is not None:
            if credentials.method == "client_credentials":
                _attributes[TelemetryAttributes.fga_client_request_client_id] = (
                    credentials.configuration.client_id
                )

        return _attributes

    @staticmethod
    def fromResponse(
        response: (
            HTTPResponse | RESTResponse | ClientResponse | ApiException | None
        ) = None,
        credentials: Credentials | None = None,
        attributes: dict[TelemetryAttribute, str | bool | int | float] | None = None,
        start: float | None = None,
    ) -> dict[TelemetryAttribute, str | bool | int | float]:
        response_model_id = None
        response_query_duration = None
        _attributes: dict[TelemetryAttribute, str | bool | int | float] = {}

        if attributes is not None:
            _attributes = attributes

        if start is not None and start > 0:
            _attributes[TelemetryAttributes.http_client_request_duration] = int(
                (time.time() - start) * 1000
            )

        if isinstance(response, ApiException):
            if response.status is not None:
                _attributes[TelemetryAttributes.http_response_status_code] = int(
                    response.status
                )

            if response.body is not None:
                response_model_id = response.body.get(
                    "openfga-authorization-model-id"
                ) or response.body.get("openfga_authorization_model_id")
                response_query_duration = response.body.get("fga-query-duration-ms")

        if response is not None:
            if hasattr(response, "status"):
                _attributes[TelemetryAttributes.http_response_status_code] = int(
                    response.status
                )

            if hasattr(response, "getheader") and callable(response.getheader):
                response_model_id = response.getheader("openfga-authorization-model-id")
                response_query_duration = response.getheader("fga-query-duration-ms")

            if hasattr(response, "headers"):
                response_model_id = response.headers.get(
                    "openfga-authorization-model-id"
                )
                response_query_duration = response.headers.get("fga-query-duration-ms")

        if response_model_id is not None:
            _attributes[TelemetryAttributes.fga_client_response_model_id] = (
                response_model_id
            )

        if response_query_duration is not None:
            _attributes[TelemetryAttributes.http_server_request_duration] = (
                response_query_duration
            )

        if isinstance(credentials, Credentials):
            if credentials.method == "client_credentials":
                _attributes[TelemetryAttributes.fga_client_request_client_id] = (
                    credentials.configuration.client_id
                )

        return _attributes

    @staticmethod
    def coalesceAttributeValue(
        attribute: TelemetryAttribute,
        value: str | bool | int | float | None = None,
        attributes: dict[TelemetryAttribute, str | bool | int | float] | None = None,
    ) -> str | bool | int | float | None:
        _value: str | bool | int | float | None = None

        if value is not None:
            _value = value
        else:
            if attributes is not None and attribute in attributes.keys():
                _value = attributes.get(attribute)

        if _value is not None:
            if attribute.format == "int":
                try:
                    return int(_value)
                except Exception:
                    pass
            elif attribute.format == "float":
                try:
                    return float(_value)
                except Exception:
                    pass
            elif attribute.format == "string":
                try:
                    return str(_value)
                except Exception:
                    pass

        return None
