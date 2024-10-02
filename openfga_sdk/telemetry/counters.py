from typing import NamedTuple


class TelemetryCounter(NamedTuple):
    name: str
    unit: str
    description: str


class TelemetryCounters:
    credentials_request: TelemetryCounter = TelemetryCounter(
        name="fga-client.credentials.request",
        unit="milliseconds",
        description="The number of times an access token is requested.",
    )
