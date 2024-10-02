from openfga_sdk.telemetry.counters import TelemetryCounter, TelemetryCounters


def test_telemetry_counter_initialization():
    counter = TelemetryCounter(
        name="fga-client.test.counter",
        unit="seconds",
        description="A test counter for unit testing.",
    )

    assert counter.name == "fga-client.test.counter"
    assert counter.unit == "seconds"
    assert counter.description == "A test counter for unit testing."


def test_telemetry_counters_default_values():
    counters = TelemetryCounters()

    assert counters.credentials_request.name == "fga-client.credentials.request"
    assert counters.credentials_request.unit == "milliseconds"
    assert (
        counters.credentials_request.description
        == "The number of times an access token is requested."
    )


def test_telemetry_counters_custom_counter():
    custom_counter = TelemetryCounter(
        name="fga-client.custom.counter",
        unit="operations",
        description="A custom counter for specific operations.",
    )

    assert custom_counter.name == "fga-client.custom.counter"
    assert custom_counter.unit == "operations"
    assert custom_counter.description == "A custom counter for specific operations."
