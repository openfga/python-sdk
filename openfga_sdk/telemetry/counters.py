from typing import NamedTuple, Optional


class TelemetryCounter(NamedTuple):
    name: str
    description: str
    unit: str = ""


class TelemetryCounters:
    fga_client_credentials_request: TelemetryCounter = TelemetryCounter(
        name="fga-client.credentials.request",
        description="Total number of new token requests initiated using the Client Credentials flow.",
    )

    fga_client_request: TelemetryCounter = TelemetryCounter(
        name="fga-client.request",
        description="Total number of requests made to the FGA server.",
    )

    _counters: list[TelemetryCounter] = [
        fga_client_credentials_request,
        fga_client_request,
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
