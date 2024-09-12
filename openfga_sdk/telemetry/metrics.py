from typing import Optional

from opentelemetry.metrics import Counter, Histogram, Meter, get_meter

from openfga_sdk import __version__
from openfga_sdk.telemetry.attributes import TelemetryAttribute, TelemetryAttributes
from openfga_sdk.telemetry.configuration import (
    TelemetryConfiguration,
    TelemetryMetricsConfiguration,
)
from openfga_sdk.telemetry.counters import TelemetryCounter, TelemetryCounters
from openfga_sdk.telemetry.histograms import TelemetryHistogram, TelemetryHistograms


class MetricsTelemetry:
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
            self._meter = get_meter("openfga-sdk", __version__)

        return self._meter

    def counter(
        self,
        counter: str | TelemetryCounter,
        value: int = None,
        attributes: dict[TelemetryAttribute | str, str | int] | None = None,
    ) -> Counter:
        if isinstance(counter, str):
            try:
                counter = TelemetryCounters[counter]
            except (KeyError, TypeError):
                raise KeyError(f"Invalid counter key: {counter}")

        if not isinstance(counter, TelemetryCounter):
            raise ValueError(
                "counter must be a TelemetryCounter, or a string that is a key in TelemetryCounters"
            )

        if counter.name not in self._counters:
            self._counters[counter.name] = self.meter().create_counter(
                name=counter.name, unit=counter.unit, description=counter.description
            )

        if value is not None:
            self._counters[counter.name].add(amount=value, attributes=attributes)

        return self._counters[counter.name]

    def histogram(
        self,
        histogram: str | TelemetryHistogram,
        value: int | float = None,
        attributes: dict[TelemetryAttribute | str, str | int] | None = None,
    ) -> Histogram:
        if isinstance(histogram, str):
            try:
                histogram = TelemetryHistograms[histogram]
            except (KeyError, TypeError):
                raise KeyError(f"Invalid histogram key: {histogram}")

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

        if value is not None:
            self._histograms[histogram.name].record(amount=value, attributes=attributes)

        return self._histograms[histogram.name]

    def credentialsRequest(
        self,
        value: int | float | None = None,
        attributes: dict[TelemetryAttribute | str, str | int] | None = None,
        configuration: TelemetryConfiguration | None = None,
    ) -> Counter:
        if configuration is None:
            configuration = TelemetryConfiguration()

        if (
            isinstance(configuration, TelemetryMetricsConfiguration) is False
            or configuration.metrics.counter_credentials_request.enabled is False
            or configuration.metrics.counter_credentials_request.attributes() == {}
        ):
            return self.counter(TelemetryCounters.credentials_request)

        attributes = TelemetryAttributes().prepare(
            attributes,
            filter=configuration.metrics.counter_credentials_request.attributes(),
        )

        return self.counter(TelemetryCounters.credentials_request, value, attributes)

    def requestDuration(
        self,
        value: int | float | None = None,
        attributes: dict[TelemetryAttribute | str, str | int] | None = None,
        configuration: TelemetryConfiguration | None = None,
    ) -> Histogram:
        if configuration is None:
            configuration = TelemetryConfiguration()

        if (
            isinstance(configuration, TelemetryConfiguration) is False
            or configuration.metrics.histogram_request_duration.enabled is False
            or configuration.metrics.histogram_request_duration.attributes() == {}
        ):
            return self.histogram(TelemetryHistograms.request_duration)

        if (
            value is None
            and TelemetryAttributes.http_client_request_duration.name in attributes
        ):
            value = attributes[TelemetryAttributes.http_client_request_duration.name]
            attributes.pop(TelemetryAttributes.http_client_request_duration.name, None)

        if value is not None:
            try:
                value = int(value)
                attributes[TelemetryAttributes.http_client_request_duration.name] = (
                    value
                )
            except ValueError:
                value = None

        attributes = TelemetryAttributes().prepare(
            attributes,
            filter=configuration.metrics.histogram_request_duration.attributes(),
        )

        if (
            value is None
            and TelemetryAttributes.http_client_request_duration.name in attributes
        ):
            value = attributes[TelemetryAttributes.http_client_request_duration.name]

        if value is None:
            return self.histogram(TelemetryHistograms.request_duration)

        return self.histogram(TelemetryHistograms.request_duration, value, attributes)

    def queryDuration(
        self,
        value: int | float | None = None,
        attributes: dict[TelemetryAttribute | str, str | int] | None = None,
        configuration: TelemetryConfiguration | None = None,
    ) -> Histogram:
        if configuration is None:
            configuration = TelemetryConfiguration()

        if (
            isinstance(configuration, TelemetryConfiguration) is False
            or configuration.metrics.histogram_query_duration.enabled is False
            or configuration.metrics.histogram_query_duration.attributes() == {}
        ):
            return self.histogram(TelemetryHistograms.query_duration)

        if (
            value is None
            and TelemetryAttributes.http_server_request_duration.name in attributes
        ):
            value = attributes[TelemetryAttributes.http_server_request_duration.name]
            attributes.pop(TelemetryAttributes.http_server_request_duration.name, None)

        if value is not None:
            try:
                value = int(value)
                attributes[TelemetryAttributes.http_server_request_duration.name] = (
                    value
                )
            except ValueError:
                value = None

        attributes = TelemetryAttributes().prepare(
            attributes,
            filter=configuration.metrics.histogram_query_duration.attributes(),
        )

        if value is None:
            return self.histogram(TelemetryHistograms.query_duration)

        return self.histogram(TelemetryHistograms.query_duration, value, attributes)
