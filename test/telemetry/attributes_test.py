import time

from unittest.mock import MagicMock

import pytest

from urllib3 import HTTPResponse

from openfga_sdk.credentials import CredentialConfiguration, Credentials
from openfga_sdk.models.batch_check_request import BatchCheckRequest
from openfga_sdk.models.check_request import CheckRequest
from openfga_sdk.rest import RESTResponse
from openfga_sdk.telemetry.attributes import (
    TelemetryAttributes,
)


@pytest.fixture
def telemetry_attributes():
    return TelemetryAttributes()


def test_prepare_with_valid_attributes(telemetry_attributes):
    attributes = {
        telemetry_attributes.fga_client_request_client_id: "client_123",
        telemetry_attributes.http_request_method: "GET",
        telemetry_attributes.fga_client_request_batch_check_size: 3,
    }
    filter_attributes = [
        telemetry_attributes.fga_client_request_client_id,
        telemetry_attributes.fga_client_request_batch_check_size,
    ]

    prepared = telemetry_attributes.prepare(attributes, filter=filter_attributes)

    # Assert that only filtered attributes are returned
    assert prepared == {
        "fga-client.request.client_id": "client_123",
        "fga-client.request.batch_check_size": 3,
    }


def test_prepare_with_empty_attributes(telemetry_attributes):
    attributes = {}
    prepared = telemetry_attributes.prepare(attributes)
    assert prepared == {}


def test_prepare_with_none_attributes(telemetry_attributes):
    prepared = telemetry_attributes.prepare(None)
    assert prepared == {}


def test_prepare_with_invalid_attributes(telemetry_attributes):
    attributes = {
        "invalid_attribute": "value",
    }
    filters = [telemetry_attributes.fga_client_request_client_id]

    with pytest.raises(ValueError):
        telemetry_attributes.prepare(attributes, filter=filters)


def test_from_request_with_all_params(telemetry_attributes):
    credentials = Credentials(
        method="client_credentials",
        configuration=CredentialConfiguration(client_id="client_123"),
    )
    start_time = time.time() - 5  # Simulate a request started 5 seconds ago

    attributes = telemetry_attributes.fromRequest(
        user_agent="TestAgent",
        fga_method="FGA_METHOD",
        http_method="POST",
        url="https://example.com/api",
        resend_count=2,
        start=start_time,
        credentials=credentials,
    )

    assert attributes[TelemetryAttributes.fga_client_request_method] == "FgaMethod"
    assert attributes[TelemetryAttributes.user_agent_original] == "TestAgent"
    assert attributes[TelemetryAttributes.http_host] == "example.com"
    assert attributes[TelemetryAttributes.http_request_method] == "POST"
    assert attributes[TelemetryAttributes.url_scheme] == "https"
    assert attributes[TelemetryAttributes.url_full] == "https://example.com/api"

    assert TelemetryAttributes.http_client_request_duration in attributes
    assert attributes[TelemetryAttributes.http_request_resend_count] == 2
    assert attributes[TelemetryAttributes.fga_client_request_client_id] == "client_123"


def test_from_request_without_optional_params(telemetry_attributes):
    attributes = telemetry_attributes.fromRequest(
        user_agent="MinimalAgent",
        fga_method="FGA_METHOD",
        http_method="GET",
        url="http://minimal.com",
    )

    assert attributes[TelemetryAttributes.fga_client_request_method] == "FgaMethod"
    assert attributes[TelemetryAttributes.user_agent_original] == "MinimalAgent"
    assert attributes[TelemetryAttributes.http_host] == "minimal.com"
    assert attributes[TelemetryAttributes.http_request_method] == "GET"
    assert attributes[TelemetryAttributes.url_scheme] == "http"
    assert attributes[TelemetryAttributes.url_full] == "http://minimal.com"

    assert TelemetryAttributes.http_client_request_duration not in attributes
    assert TelemetryAttributes.http_request_resend_count not in attributes
    assert TelemetryAttributes.fga_client_request_client_id not in attributes


def test_from_response_with_http_response(telemetry_attributes):
    start_time = time.time() - 5
    response = MagicMock(spec=HTTPResponse)
    response.status = 200
    response.getheader.side_effect = lambda header: {
        "openfga-authorization-model-id": "model_123",
        "fga-query-duration-ms": "50",
    }.get(header)

    credentials = Credentials(
        method="client_credentials",
        configuration=CredentialConfiguration(client_id="client_123"),
    )
    attributes = telemetry_attributes.fromResponse(
        response=response,
        credentials=credentials,
        start=start_time,
    )

    assert attributes[TelemetryAttributes.http_response_status_code] == 200
    assert attributes[TelemetryAttributes.fga_client_response_model_id] == "model_123"
    assert attributes[TelemetryAttributes.http_server_request_duration] == "50"
    assert attributes[TelemetryAttributes.fga_client_request_client_id] == "client_123"
    assert TelemetryAttributes.http_client_request_duration in attributes
    assert attributes[TelemetryAttributes.http_client_request_duration] > 0


def test_from_response_with_rest_response(telemetry_attributes):
    start_time = time.time() - 5
    response = MagicMock(spec=RESTResponse)
    response.status = 404
    response.headers = {
        "openfga-authorization-model-id": "model_404",
        "fga-query-duration-ms": "100",
    }

    response.getheader = lambda key: response.headers.get(key)

    credentials = Credentials(
        method="client_credentials",
        configuration=CredentialConfiguration(client_id="client_456"),
    )
    attributes = telemetry_attributes.fromResponse(
        response=response,
        credentials=credentials,
        start=start_time,
    )

    assert attributes[TelemetryAttributes.http_response_status_code] == 404
    assert attributes[TelemetryAttributes.fga_client_response_model_id] == "model_404"
    assert attributes[TelemetryAttributes.http_server_request_duration] == "100"
    assert attributes[TelemetryAttributes.fga_client_request_client_id] == "client_456"
    assert TelemetryAttributes.http_client_request_duration in attributes
    assert attributes[TelemetryAttributes.http_client_request_duration] > 0


def test_from_body_with_batch_check(telemetry_attributes):
    body = MagicMock(spec=BatchCheckRequest)
    body.checks = ["1", "2", "3"]

    attributes = telemetry_attributes.fromBody(body=body)

    assert attributes[TelemetryAttributes.fga_client_request_batch_check_size] == 3


def test_from_body_with_other_body(telemetry_attributes):
    body = MagicMock(spec=CheckRequest)

    attributes = telemetry_attributes.fromBody(body=body)

    assert attributes == {}
