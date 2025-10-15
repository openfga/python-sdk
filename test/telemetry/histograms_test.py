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

    assert histograms.fga_client_request_duration.name == "fga-client.request.duration"
    assert histograms.fga_client_request_duration.unit == "milliseconds"
    assert (
        histograms.fga_client_request_duration.description
        == "Total request time for FGA requests, in milliseconds."
    )

    assert histograms.fga_client_query_duration.name == "fga-client.query.duration"
    assert histograms.fga_client_query_duration.unit == "milliseconds"
    assert (
        histograms.fga_client_query_duration.description
        == "Time taken by the FGA server to process and evaluate the request, in milliseconds."
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
