from openfga_sdk.telemetry.histograms import TelemetryHistogram, TelemetryHistograms


def test_telemetry_histogram_initialization():
    histogram = TelemetryHistogram(
        name="fga-client.test.histogram",
        unit="seconds",
        description="A test histogram for unit testing.",
    )

    assert histogram.name == "fga-client.test.histogram"
    assert histogram.unit == "seconds"
    assert histogram.description == "A test histogram for unit testing."


def test_telemetry_histograms_default_values():
    histograms = TelemetryHistograms()

    assert histograms.request_duration.name == "fga-client.request.duration"
    assert histograms.request_duration.unit == "milliseconds"
    assert (
        histograms.request_duration.description
        == "How long it took for a request to be fulfilled."
    )

    assert histograms.query_duration.name == "fga-client.query.duration"
    assert histograms.query_duration.unit == "milliseconds"
    assert (
        histograms.query_duration.description
        == "How long it took to perform a query request."
    )


def test_telemetry_histograms_custom_histogram():
    custom_histogram = TelemetryHistogram(
        name="fga-client.custom.histogram",
        unit="operations",
        description="A custom histogram for specific operations.",
    )

    assert custom_histogram.name == "fga-client.custom.histogram"
    assert custom_histogram.unit == "operations"
    assert custom_histogram.description == "A custom histogram for specific operations."
