from typing import NamedTuple


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
    def getAll() -> list[TelemetryCounter]:
        return TelemetryCounters._counters

    @staticmethod
    def get(
        name: str | None = None,
    ) -> TelemetryCounter | None:
        for counter in TelemetryCounters._counters:
            if counter.name == name:
                return counter

        return None
