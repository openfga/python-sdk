from unittest.mock import MagicMock, patch

import pytest
from opentelemetry.metrics import Counter, Histogram, Meter

from openfga_sdk import __version__
from openfga_sdk.telemetry.attributes import TelemetryAttributes
from openfga_sdk.telemetry.counters import TelemetryCounters
from openfga_sdk.telemetry.histograms import TelemetryHistograms
from openfga_sdk.telemetry.metrics import MetricsTelemetry


@patch("openfga_sdk.telemetry.metrics.get_meter")
def test_meter_lazy_initialization(mock_get_meter):
    mock_meter = MagicMock(spec=Meter)
    mock_get_meter.return_value = mock_meter

    telemetry = MetricsTelemetry()

    # Ensure _meter is initially None
    assert telemetry._meter is None

    # Access the meter property, which should trigger lazy initialization
    meter = telemetry.meter()
    assert meter == mock_meter
    mock_get_meter.assert_called_once_with("openfga-sdk", __version__)

    # Access the meter property again, no new instance should be created
    meter_again = telemetry.meter()
    assert meter_again == meter
    mock_get_meter.assert_called_once()


@patch("openfga_sdk.telemetry.metrics.get_meter")
def test_counter_creation_and_add(mock_get_meter):
    mock_meter = MagicMock(spec=Meter)
    mock_counter = MagicMock(spec=Counter)
    mock_get_meter.return_value = mock_meter
    mock_meter.create_counter.return_value = mock_counter

    telemetry = MetricsTelemetry()

    attributes = {
        TelemetryAttributes.fga_client_request_model_id.name: "model_123",
        "custom_attribute": "custom_value",
    }

    counter = telemetry.counter(
        TelemetryCounters.credentials_request, value=5, attributes=attributes
    )

    assert counter == mock_counter

    telemetry._meter.create_counter.assert_called_once_with(
        name=TelemetryCounters.credentials_request.name,
        unit=TelemetryCounters.credentials_request.unit,
        description=TelemetryCounters.credentials_request.description,
    )

    mock_counter.add.assert_called_once_with(amount=5, attributes=attributes)


@patch("openfga_sdk.telemetry.metrics.get_meter")
def test_histogram_creation_and_record(mock_get_meter):
    mock_meter = MagicMock(spec=Meter)
    mock_histogram = MagicMock(spec=Histogram)
    mock_get_meter.return_value = mock_meter
    mock_meter.create_histogram.return_value = mock_histogram

    telemetry = MetricsTelemetry()

    attributes = {
        TelemetryAttributes.fga_client_request_model_id.name: "model_123",
        "custom_attribute": "custom_value",
    }

    histogram = telemetry.histogram(
        TelemetryHistograms.request_duration, value=200.5, attributes=attributes
    )

    assert histogram == mock_histogram

    telemetry._meter.create_histogram.assert_called_once_with(
        name=TelemetryHistograms.request_duration.name,
        unit=TelemetryHistograms.request_duration.unit,
        description=TelemetryHistograms.request_duration.description,
    )

    mock_histogram.record.assert_called_once_with(amount=200.5, attributes=attributes)


def test_invalid_counter_key():
    telemetry = MetricsTelemetry()
    with pytest.raises(KeyError):
        telemetry.counter("invalid_counter_key")


def test_invalid_histogram_key():
    telemetry = MetricsTelemetry()
    with pytest.raises(KeyError):
        telemetry.histogram("invalid_histogram_key")
