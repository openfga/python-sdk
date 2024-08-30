from openfga_sdk.telemetry.metrics import MetricsTelemetry


class Telemetry:
    _metrics: MetricsTelemetry = None

    def metrics(self) -> MetricsTelemetry:
        if self._metrics is None:
            self._metrics = MetricsTelemetry()

        return self._metrics
