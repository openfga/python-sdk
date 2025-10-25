from typing import NamedTuple


class TelemetryHistogram(NamedTuple):
    name: str
    description: str
    unit: str = "milliseconds"


class TelemetryHistograms:
    fga_client_request_duration: TelemetryHistogram = TelemetryHistogram(
        name="fga-client.request.duration",
        description="Total request time for FGA requests, in milliseconds.",
    )
    fga_client_query_duration: TelemetryHistogram = TelemetryHistogram(
        name="fga-client.query.duration",
        description="Time taken by the FGA server to process and evaluate the request, in milliseconds.",
    )

    _histograms: list[TelemetryHistogram] = [
        fga_client_request_duration,
        fga_client_query_duration,
    ]

    @staticmethod
    def getAll() -> list[TelemetryHistogram]:
        return TelemetryHistograms._histograms

    @staticmethod
    def get(
        name: str | None = None,
    ) -> TelemetryHistogram | None:
        for histogram in TelemetryHistograms._histograms:
            if histogram.name == name:
                return histogram

        return None
