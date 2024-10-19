from typing import Optional

from opentelemetry.metrics import Counter, Histogram, Meter, get_meter

from openfga_sdk.telemetry.attributes import (
    TelemetryAttribute,
    TelemetryAttributes,
)
from openfga_sdk.telemetry.configuration import (
    TelemetryConfiguration,
    isMetricEnabled,
)
from openfga_sdk.telemetry.counters import TelemetryCounter, TelemetryCounters
from openfga_sdk.telemetry.histograms import TelemetryHistogram, TelemetryHistograms


class TelemetryMetrics:
    _meter: Meter = None
    _histograms: dict[str, Histogram] = {}
    _counters: dict[str, Counter] = {}

    def __init__(
        self,
        meter: Optional[Meter] = None,
        counters: Optional[dict[str, Counter]] = None,
        histograms: Optional[dict[str, Histogram]] = None,
    ):
        self._meter = meter
        self._counters = counters or {}
        self._histograms = histograms or {}

    def meter(self) -> Meter:
        if self._meter is None:
            self._meter = get_meter("openfga-sdk")

        return self._meter

    def counter(self, counter: TelemetryCounter) -> Counter:
        if not isinstance(counter, TelemetryCounter):
            raise ValueError(
                "counter must be a TelemetryCounter, or a string that is a key in TelemetryCounters"
            )

        if counter.name not in self._counters:
            self._counters[counter.name] = self.meter().create_counter(
                name=counter.name, unit=counter.unit, description=counter.description
            )

        return self._counters[counter.name]

    def histogram(self, histogram: TelemetryHistogram) -> Histogram:
        if not isinstance(histogram, TelemetryHistogram):
            raise ValueError(
                "histogram must be a TelemetryHistogram, or a string that is a key in TelemetryHistograms"
            )

        if histogram.name not in self._histograms:
            self._histograms[histogram.name] = self.meter().create_histogram(
                name=histogram.name,
                unit=histogram.unit,
                description=histogram.description,
            )

        return self._histograms[histogram.name]

    def request(
        self,
        value: int = 1,
        attributes: dict[TelemetryAttribute, str | int] | None = None,
        configuration: TelemetryConfiguration | None = None,
    ) -> Counter:
        """
        Record a request made by the client.
        """
        counter = self.counter(TelemetryCounters.fga_client_request)

        if isMetricEnabled(configuration, TelemetryCounters.fga_client_request):
            attributes = TelemetryAttributes.prepare(
                attributes,
                filter=configuration.metrics.fga_client_request.getAttributes(),
            )

            if value is not None:
                counter.add(amount=value, attributes=attributes)

        return counter

    def credentialsRequest(
        self,
        value: int = 1,
        attributes: dict[TelemetryAttribute, str | int] | None = None,
        configuration: TelemetryConfiguration | None = None,
    ) -> Counter:
        """
        Record a client credentials request made by the client.
        """
        counter = self.counter(TelemetryCounters.fga_client_credentials_request)

        if isMetricEnabled(
            configuration, TelemetryCounters.fga_client_credentials_request
        ):
            attributes = TelemetryAttributes.prepare(
                attributes,
                filter=configuration.metrics.fga_client_credentials_request.getAttributes(),
            )

            if value is not None:
                counter.add(amount=value, attributes=attributes)

        return counter

    def requestDuration(
        self,
        value: int | float | None = None,
        attributes: dict[TelemetryAttribute, str | int] | None = None,
        configuration: TelemetryConfiguration | None = None,
    ) -> Histogram:
        """
        Record the duration of a request made by the client.
        """
        histogram = self.histogram(TelemetryHistograms.fga_client_request_duration)

        if isMetricEnabled(
            configuration, TelemetryHistograms.fga_client_request_duration
        ):
            attributes[TelemetryAttributes.http_client_request_duration] = value = (
                TelemetryAttributes.coalesceAttributeValue(
                    TelemetryAttributes.http_client_request_duration,
                    value,
                    attributes,
                )
            )

            attributes = TelemetryAttributes.prepare(
                attributes,
                filter=configuration.metrics.fga_client_request_duration.getAttributes(),
            )

            if value is not None:
                histogram.record(amount=value, attributes=attributes)

        return histogram

    def queryDuration(
        self,
        value: int | float | None = None,
        attributes: dict[TelemetryAttribute, str | int] | None = None,
        configuration: TelemetryConfiguration | None = None,
    ) -> Histogram:
        """
        Record the duration of a query made by the client, as reported by the server.
        """
        histogram = self.histogram(TelemetryHistograms.fga_client_query_duration)

        if isMetricEnabled(
            configuration, TelemetryHistograms.fga_client_query_duration
        ):
            attributes[TelemetryAttributes.http_server_request_duration] = value = (
                TelemetryAttributes.coalesceAttributeValue(
                    TelemetryAttributes.http_server_request_duration,
                    value,
                    attributes,
                )
            )

            attributes = TelemetryAttributes.prepare(
                attributes,
                filter=configuration.metrics.fga_client_query_duration.getAttributes(),
            )

            if value is not None:
                histogram.record(amount=value, attributes=attributes)

        return histogram
