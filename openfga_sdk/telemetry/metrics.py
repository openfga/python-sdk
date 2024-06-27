from opentelemetry.metrics import Histogram, Meter, get_meter

from openfga_sdk import __version__
from openfga_sdk.telemetry.histograms import TelemetryHistogram, TelemetryHistograms


class MetricsTelemetry:
    _meter: Meter = None
    _histograms: dict[str, Histogram] = {}

    def __init__(self):
        self._meter = get_meter(__name__, __version__)
        self._histograms = {}

    def meter(self) -> Meter:
        return self._meter

    def histogram(self, histogram: str | TelemetryHistogram) -> Histogram:
        if isinstance(histogram, str):
            histogram = TelemetryHistograms[histogram]

        if not isinstance(histogram, TelemetryHistogram):
            raise ValueError(
                "histogram must be a TelemetryHistogram, or a string that is a key in TelemetryHistograms"
            )

        if histogram.name not in self._histograms:
            self._histograms[histogram.name] = self._meter.create_histogram(
                histogram.name, histogram.description, histogram.unit
            )

        return self._histograms[histogram.name]
