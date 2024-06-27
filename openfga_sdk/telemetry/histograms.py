from typing import NamedTuple


class TelemetryHistogram(NamedTuple):
    name: str
    unit: str
    description: str


class TelemetryHistograms:
    duration: TelemetryHistogram = TelemetryHistogram(
        name="fga-client.request.duration",
        unit="milliseconds",
        description="The duration of requests",
    )
    query_duration: TelemetryHistogram = TelemetryHistogram(
        name="fga-client.query.duration",
        unit="milliseconds",
        description="The duration of queries on the FGA server",
    )
