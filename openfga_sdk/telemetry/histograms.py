from typing import NamedTuple, Optional


class TelemetryHistogram(NamedTuple):
    name: str
    unit: str
    description: str


class TelemetryHistograms:
    fga_client_request_duration: TelemetryHistogram = TelemetryHistogram(
        name="fga-client.request.duration",
        unit="milliseconds",
        description="Total request time for FGA requests, in milliseconds.",
    )
    fga_client_query_duration: TelemetryHistogram = TelemetryHistogram(
        name="fga-client.query.duration",
        unit="milliseconds",
        description="Time taken by the FGA server to process and evaluate the request, in milliseconds.",
    )

    _histograms: list[TelemetryHistogram] = [
        fga_client_request_duration,
        fga_client_query_duration,
    ]

    @staticmethod
    def get(
        name: Optional[str] = None,
    ) -> list[TelemetryHistogram] | TelemetryHistogram | None:
        if name is None:
            return TelemetryHistograms._histograms

        for histogram in TelemetryHistograms._histograms:
            if histogram.name == name:
                return histogram

        return None
