from opentelemetry.metrics import Counter, Histogram, Meter, get_meter

from openfga_sdk import __version__
from openfga_sdk.telemetry.attributes import TelemetryAttribute, TelemetryAttributes
from openfga_sdk.telemetry.counters import TelemetryCounter, TelemetryCounters
from openfga_sdk.telemetry.histograms import TelemetryHistogram, TelemetryHistograms


class MetricsTelemetry:
    _meter: Meter = None
    _histograms: dict[str, Histogram] = {}
    _counters: dict[str, Counter] = {}

    def __init__(self):
        self._meter = get_meter("openfga-sdk", __version__)
        self._histograms = {}

    def meter(self) -> Meter:
        return self._meter

    def counter(
        self,
        counter: str | TelemetryCounter,
        value: int = None,
        attributes: dict[TelemetryAttribute | str, str | int] | None = None,
    ) -> Counter:
        if isinstance(counter, str):
            counter = TelemetryCounters[counter]

        if not isinstance(counter, TelemetryCounter):
            raise ValueError(
                "counter must be a TelemetryCounter, or a string that is a key in TelemetryCounters"
            )

        if counter.name not in self._counters:
            self._counters[counter.name] = self._meter.create_counter(
                name=counter.name, unit=counter.unit, description=counter.description
            )

        if value is not None:
            self._counters[counter.name].add(
                amount=value, attributes=TelemetryAttributes().prepare(attributes)
            )

        return self._counters[counter.name]

    def histogram(
        self,
        histogram: str | TelemetryHistogram,
        value: int | float = None,
        attributes: dict[TelemetryAttribute | str, str | int] | None = None,
    ) -> Histogram:
        if isinstance(histogram, str):
            histogram = TelemetryHistograms[histogram]

        if not isinstance(histogram, TelemetryHistogram):
            raise ValueError(
                "histogram must be a TelemetryHistogram, or a string that is a key in TelemetryHistograms"
            )

        if histogram.name not in self._histograms:
            self._histograms[histogram.name] = self._meter.create_histogram(
                name=histogram.name,
                unit=histogram.unit,
                description=histogram.description,
            )

        if value is not None:
            self._histograms[histogram.name].record(
                amount=value, attributes=TelemetryAttributes().prepare(attributes)
            )

        return self._histograms[histogram.name]

    def credentialsRequest(
        self,
        value: int | float = None,
        attributes: dict[TelemetryAttribute | str, str | int] | None = None,
    ) -> Counter:
        return self.counter(TelemetryCounters.credentials_request, value, attributes)

    def requestDuration(
        self,
        value: int | float = None,
        attributes: dict[TelemetryAttribute | str, str | int] | None = None,
    ) -> Histogram:
        return self.histogram(TelemetryHistograms.duration, value, attributes)

    def queryDuration(
        self,
        value: int | float = None,
        attributes: dict[TelemetryAttribute | str, str | int] | None = None,
    ) -> Histogram:
        return self.histogram(TelemetryHistograms.query_duration, value, attributes)
