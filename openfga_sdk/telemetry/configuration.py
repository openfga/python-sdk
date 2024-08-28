from typing import Optional

from openfga_sdk.telemetry.attributes import TelemetryAttributes


class TelemetryMetricConfiguration:
    _enabled: bool

    def __init__(
        self,
        enabled: Optional[bool] = True,
        attr_fga_client_request_client_id: Optional[bool] = True,
        attr_fga_client_request_method: Optional[bool] = True,
        attr_fga_client_request_model_id: Optional[bool] = True,
        attr_fga_client_request_store_id: Optional[bool] = True,
        attr_fga_client_response_model_id: Optional[bool] = True,
        attr_fga_client_user: Optional[bool] = False,
        attr_http_client_request_duration: Optional[bool] = False,
        attr_http_host: Optional[bool] = True,
        attr_http_request_method: Optional[bool] = True,
        attr_http_request_resend_count: Optional[bool] = True,
        attr_http_response_status_code: Optional[bool] = True,
        attr_http_server_request_duration: Optional[bool] = False,
        attr_http_url_scheme: Optional[bool] = True,
        attr_http_url_full: Optional[bool] = True,
        attr_user_agent_original: Optional[bool] = True,
    ):
        self._enabled = enabled
        self.attr_fga_client_request_client_id = attr_fga_client_request_client_id
        self.attr_fga_client_request_method = attr_fga_client_request_method
        self.attr_fga_client_request_model_id = attr_fga_client_request_model_id
        self.attr_fga_client_request_store_id = attr_fga_client_request_store_id
        self.attr_fga_client_response_model_id = attr_fga_client_response_model_id
        self.attr_fga_client_user = attr_fga_client_user
        self.attr_http_client_request_duration = attr_http_client_request_duration
        self.attr_http_host = attr_http_host
        self.attr_http_request_method = attr_http_request_method
        self.attr_http_request_resend_count = attr_http_request_resend_count
        self.attr_http_response_status_code = attr_http_response_status_code
        self.attr_http_server_request_duration = attr_http_server_request_duration
        self.attr_http_url_scheme = attr_http_url_scheme
        self.attr_http_url_full = attr_http_url_full
        self.attr_user_agent_original = attr_user_agent_original

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        self._enabled = value

    def attributes(self) -> dict[str]:
        enabled = {}

        if self.attr_fga_client_request_client_id:
            enabled[TelemetryAttributes.fga_client_request_client_id.name] = True

        if self.attr_fga_client_request_method:
            enabled[TelemetryAttributes.fga_client_request_method.name] = True

        if self.attr_fga_client_request_model_id:
            enabled[TelemetryAttributes.fga_client_request_model_id.name] = True

        if self.attr_fga_client_request_store_id:
            enabled[TelemetryAttributes.fga_client_request_store_id.name] = True

        if self.attr_fga_client_response_model_id:
            enabled[TelemetryAttributes.fga_client_response_model_id.name] = True

        if self.attr_fga_client_user:
            enabled[TelemetryAttributes.fga_client_user.name] = True

        if self.attr_http_client_request_duration:
            enabled[TelemetryAttributes.http_client_request_duration.name] = True

        if self.attr_http_host:
            enabled[TelemetryAttributes.http_host.name] = True

        if self.attr_http_request_method:
            enabled[TelemetryAttributes.http_request_method.name] = True

        if self.attr_http_request_resend_count:
            enabled[TelemetryAttributes.http_request_resend_count.name] = True

        if self.attr_http_response_status_code:
            enabled[TelemetryAttributes.http_response_status_code.name] = True

        if self.attr_http_server_request_duration:
            enabled[TelemetryAttributes.http_server_request_duration.name] = True

        if self.attr_http_url_scheme:
            enabled[TelemetryAttributes.url_scheme.name] = True

        if self.attr_http_url_full:
            enabled[TelemetryAttributes.url_full.name] = True

        if self.attr_user_agent_original:
            enabled[TelemetryAttributes.user_agent_original.name] = True

        return enabled


class TelemetryMetricsConfiguration:
    _counter_credentials_request: TelemetryMetricConfiguration
    _histogram_request_duration: TelemetryMetricConfiguration
    _histogram_query_duration: TelemetryMetricConfiguration

    def __init__(
        self,
        counter_credentials_request: Optional[TelemetryMetricConfiguration] = None,
        histogram_request_duration: Optional[TelemetryMetricConfiguration] = None,
        histogram_query_duration: Optional[TelemetryMetricConfiguration] = None,
    ):
        if counter_credentials_request is None:
            counter_credentials_request = TelemetryMetricConfiguration()

        if histogram_request_duration is None:
            histogram_request_duration = TelemetryMetricConfiguration()

        if histogram_query_duration is None:
            histogram_query_duration = TelemetryMetricConfiguration()

        self._counter_credentials_request = counter_credentials_request
        self._histogram_request_duration = histogram_request_duration
        self._histogram_query_duration = histogram_query_duration

    @property
    def counter_credentials_request(self) -> TelemetryMetricConfiguration:
        return self._counter_credentials_request

    @counter_credentials_request.setter
    def counter_credentials_request(self, value: TelemetryMetricConfiguration):
        self._counter_credentials_request = value

    @property
    def histogram_request_duration(self) -> TelemetryMetricConfiguration:
        return self._histogram_request_duration

    @histogram_request_duration.setter
    def histogram_request_duration(self, value: TelemetryMetricConfiguration):
        self._histogram_request_duration = value

    @property
    def histogram_query_duration(self) -> TelemetryMetricConfiguration:
        return self._histogram_query_duration

    @histogram_query_duration.setter
    def histogram_query_duration(self, value: TelemetryMetricConfiguration):
        self._histogram_query_duration = value


class TelemetryConfiguration:
    _metrics: TelemetryMetricsConfiguration

    def __init__(self, metrics: Optional[TelemetryMetricsConfiguration] = None):
        if metrics is None:
            metrics = TelemetryMetricsConfiguration()

        self._metrics = metrics

    @property
    def metrics(self) -> TelemetryMetricsConfiguration:
        return self._metrics

    @metrics.setter
    def metrics(self, value: TelemetryMetricsConfiguration):
        self._metrics = value
