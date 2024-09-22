from typing import NamedTuple, Optional


class TelemetryCounter(NamedTuple):
    name: str
    unit: str
    description: str


class TelemetryCounters:
    fga_client_credentials_request: TelemetryCounter = TelemetryCounter(
        name="fga-client.credentials.request",
        unit="milliseconds",
        description="Total number of new token requests initiated using the Client Credentials flow.",
    )

    _counters: list[TelemetryCounter] = [
        fga_client_credentials_request,
    ]

    @staticmethod
    def get(
        name: Optional[str] = None,
    ) -> list[TelemetryCounter] | TelemetryCounter | None:
        if name is None:
            return TelemetryCounters._counters

        for counter in TelemetryCounters._counters:
            if counter.name == name:
                return counter

        return None
