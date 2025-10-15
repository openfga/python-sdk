from openfga_sdk.telemetry.metrics import TelemetryMetrics


class Telemetry:
    _metrics: TelemetryMetrics | None = None

    @property
    def metrics(self) -> TelemetryMetrics:
        if self._metrics is None:
            self._metrics = TelemetryMetrics()

        return self._metrics
