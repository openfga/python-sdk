from unittest.mock import MagicMock, patch

import pytest

from opentelemetry.metrics import Counter, Histogram, Meter

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
