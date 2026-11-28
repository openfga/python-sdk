from unittest.mock import MagicMock, patch

import pytest

from opentelemetry.metrics import Counter, Histogram, Meter

from openfga_sdk.telemetry.attributes import TelemetryAttributes
from openfga_sdk.telemetry.configuration import TelemetryConfiguration
from openfga_sdk.telemetry.counters import TelemetryCounters
from openfga_sdk.telemetry.histograms import TelemetryHistograms
from openfga_sdk.telemetry.metrics import TelemetryMetrics


@patch("openfga_sdk.telemetry.metrics.get_meter")
def test_meter_lazy_initialization(mock_get_meter):
    mock_meter = MagicMock(spec=Meter)
    mock_get_meter.return_value = mock_meter

    telemetry = TelemetryMetrics()

    # Ensure _meter is initially None
    assert telemetry._meter is None

    # Access the meter property, which should trigger lazy initialization
    meter = telemetry.meter()
    assert meter == mock_meter
    mock_get_meter.assert_called_once_with("openfga-sdk")

    # Access the meter property again, no new instance should be created
    meter_again = telemetry.meter()
    assert meter_again == meter
    mock_get_meter.assert_called_once()


@patch("openfga_sdk.telemetry.metrics.get_meter")
def test_counter_creation(mock_get_meter):
    mock_meter = MagicMock(spec=Meter)
    mock_counter = MagicMock(spec=Counter)
    mock_get_meter.return_value = mock_meter
    mock_meter.create_counter.return_value = mock_counter

    telemetry = TelemetryMetrics()

    counter = telemetry.counter(TelemetryCounters.fga_client_credentials_request)

    assert counter == mock_counter

    telemetry._meter.create_counter.assert_called_once_with(
        name=TelemetryCounters.fga_client_credentials_request.name,
        unit=TelemetryCounters.fga_client_credentials_request.unit,
        description=TelemetryCounters.fga_client_credentials_request.description,
    )


@patch("openfga_sdk.telemetry.metrics.get_meter")
def test_histogram_creation(mock_get_meter):
    mock_meter = MagicMock(spec=Meter)
    mock_histogram = MagicMock(spec=Histogram)
    mock_get_meter.return_value = mock_meter
    mock_meter.create_histogram.return_value = mock_histogram

    telemetry = TelemetryMetrics()

    histogram = telemetry.histogram(TelemetryHistograms.fga_client_request_duration)

    assert histogram == mock_histogram

    telemetry._meter.create_histogram.assert_called_once_with(
        name=TelemetryHistograms.fga_client_request_duration.name,
        unit=TelemetryHistograms.fga_client_request_duration.unit,
        description=TelemetryHistograms.fga_client_request_duration.description,
    )


def test_invalid_counter_key():
    telemetry = TelemetryMetrics()
    with pytest.raises(ValueError):
        telemetry.counter("invalid_counter_key")


def test_invalid_histogram_key():
    telemetry = TelemetryMetrics()
    with pytest.raises(ValueError):
        telemetry.histogram("invalid_histogram_key")


@patch("openfga_sdk.telemetry.metrics.get_meter")
def test_batch_check_merge_counters_use_their_attribute_filters(mock_get_meter):
    mock_meter = MagicMock(spec=Meter)
    mock_counter = MagicMock(spec=Counter)
    mock_get_meter.return_value = mock_meter
    mock_meter.create_counter.return_value = mock_counter

    telemetry = TelemetryMetrics()
    configuration = TelemetryConfiguration(
        {
            "metrics": {
                "fga-client.model_cache.lookup": {
                    "fga-client.model_cache.result": True,
                },
            }
        }
    )

    telemetry.modelCacheLookup(
        attributes={
            TelemetryAttributes.fga_client_model_cache_result: "hit",
            TelemetryAttributes.fga_client_request_store_id: "store",
        },
        configuration=configuration,
    )
    mock_counter.add.assert_called_once_with(
        amount=1, attributes={"fga-client.model_cache.result": "hit"}
    )

    # Not configured, so not recorded
    mock_counter.add.reset_mock()
    telemetry.batchCheckChecksSent(2, configuration=configuration)
    telemetry.batchCheckChecksRequested(4, configuration=configuration)
    telemetry.batchCheckMergeFallback(configuration=configuration)
    mock_counter.add.assert_not_called()


@patch("openfga_sdk.telemetry.metrics.get_meter")
def test_batch_check_merge_counters_are_on_by_default(mock_get_meter):
    mock_meter = MagicMock(spec=Meter)
    mock_counter = MagicMock(spec=Counter)
    mock_get_meter.return_value = mock_meter
    mock_meter.create_counter.return_value = mock_counter

    telemetry = TelemetryMetrics()
    configuration = TelemetryConfiguration(TelemetryConfiguration.getSdkDefaults())
    attributes = {
        TelemetryAttributes.fga_client_request_store_id: "store",
        TelemetryAttributes.fga_client_request_model_id: "model",
    }

    telemetry.batchCheckChecksRequested(4, attributes, configuration)
    telemetry.batchCheckChecksSent(2, attributes, configuration)
    telemetry.batchCheckMergeFallback(
        attributes={**attributes, TelemetryAttributes.http_response_status_code: 403},
        configuration=configuration,
    )
    telemetry.modelCacheLookup(
        attributes={
            **attributes,
            TelemetryAttributes.fga_client_model_cache_result: "miss",
        },
        configuration=configuration,
    )

    expected = {
        "fga-client.request.store_id": "store",
        "fga-client.request.model_id": "model",
    }
    assert [call.kwargs for call in mock_counter.add.call_args_list] == [
        {"amount": 4, "attributes": expected},
        {"amount": 2, "attributes": expected},
        {
            "amount": 1,
            "attributes": {**expected, "http.response.status_code": 403},
        },
        {
            "amount": 1,
            "attributes": {**expected, "fga-client.model_cache.result": "miss"},
        },
    ]
