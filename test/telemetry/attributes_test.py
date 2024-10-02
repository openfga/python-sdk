import time
from unittest.mock import MagicMock

import pytest
from urllib3 import HTTPResponse

from openfga_sdk.credentials import CredentialConfiguration, Credentials
from openfga_sdk.rest import RESTResponse
from openfga_sdk.telemetry.attributes import TelemetryAttributes


@pytest.fixture
def telemetry_attributes():
    return TelemetryAttributes()


def test_prepare_with_valid_attributes(telemetry_attributes):
    attributes = {
        telemetry_attributes.fga_client_request_client_id: "client_123",
        telemetry_attributes.http_request_method: "GET",
    }
    filter_attributes = [telemetry_attributes.fga_client_request_client_id]

    prepared = telemetry_attributes.prepare(attributes, filter=filter_attributes)

    # Assert that only filtered attributes are returned
    assert prepared == {
        "fga-client.request.client_id": "client_123",
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

    assert attributes["fga-client.request.method"] == "FGA_METHOD"
    assert attributes["user_agent.original"] == "TestAgent"
    assert attributes["http.host"] == "example.com"
    assert attributes["http.request.method"] == "POST"
    assert attributes["url.scheme"] == "https"
    assert attributes["url.full"] == "https://example.com/api"
    assert "http.client.request.duration" in attributes
    assert attributes["http.request.resend_count"] == 2
    assert attributes["fga-client.request.client_id"] == "client_123"


def test_from_request_without_optional_params(telemetry_attributes):
    attributes = telemetry_attributes.fromRequest(
        user_agent="MinimalAgent",
        fga_method="FGA_METHOD",
        http_method="GET",
        url="http://minimal.com",
    )

    assert attributes["fga-client.request.method"] == "FGA_METHOD"
    assert attributes["user_agent.original"] == "MinimalAgent"
    assert attributes["http.host"] == "minimal.com"
    assert attributes["http.request.method"] == "GET"
    assert attributes["url.scheme"] == "http"
    assert attributes["url.full"] == "http://minimal.com"
    assert "http.client.request.duration" not in attributes
    assert "http.request.resend_count" not in attributes
    assert "fga-client.request.client_id" not in attributes


def test_from_response_with_http_response(telemetry_attributes):
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
        response=response, credentials=credentials
    )

    assert attributes["http.response.status_code"] == 200
    assert attributes["fga-client.response.model_id"] == "model_123"
    assert attributes["http.server.request.duration"] == "50"
    assert attributes["fga-client.request.client_id"] == "client_123"


def test_from_response_with_rest_response(telemetry_attributes):
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
        response=response, credentials=credentials
    )

    assert attributes["http.response.status_code"] == 404
    assert attributes["fga-client.response.model_id"] == "model_404"
    assert attributes["http.server.request.duration"] == "100"
    assert attributes["fga-client.request.client_id"] == "client_456"


def test_instance_has_attribute(telemetry_attributes):
    mock_instance = MagicMock(spec_set=["some_attribute"])
    mock_instance.some_attribute = "value"
    assert telemetry_attributes.instanceHasAttribute(mock_instance, "some_attribute")
    assert not telemetry_attributes.instanceHasAttribute(
        mock_instance, "missing_attribute"
    )


def test_instance_has_callable(telemetry_attributes):
    mock_instance = MagicMock(spec_set=["some_callable", "some_attribute"])
    mock_instance.some_callable = lambda: "I am callable"

    assert telemetry_attributes.instanceHasCallable(mock_instance, "some_callable")

    assert not telemetry_attributes.instanceHasCallable(
        mock_instance, "missing_callable"
    )

    mock_instance.some_attribute = "not callable"
    assert not telemetry_attributes.instanceHasCallable(mock_instance, "some_attribute")
