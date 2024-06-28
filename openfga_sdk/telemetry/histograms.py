from typing import NamedTuple


class TelemetryHistogram(NamedTuple):
    name: str
    unit: str
    description: str


class TelemetryHistograms:
    duration: TelemetryHistogram = TelemetryHistogram(
        name="fga-client.request.duration",
        unit="milliseconds",
        description="How long it took for a request to be fulfilled.",
    )
    query_duration: TelemetryHistogram = TelemetryHistogram(
        name="fga-client.query.duration",
        unit="milliseconds",
        description="How long it took to perform a query request.",
    )
