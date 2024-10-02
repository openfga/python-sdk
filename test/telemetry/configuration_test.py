from openfga_sdk.telemetry.attributes import TelemetryAttributes
from openfga_sdk.telemetry.configuration import (
    TelemetryConfiguration,
    TelemetryMetricConfiguration,
    TelemetryMetricsConfiguration,
)


def test_telemetry_metric_configuration_default_initialization():
    config = TelemetryMetricConfiguration()

    # Assert default enabled value
    assert config.enabled is True

    # Assert all attributes are True by default
    assert config.attr_fga_client_request_client_id is True
    assert config.attr_fga_client_request_method is True
    assert config.attr_fga_client_request_model_id is True
    assert config.attr_fga_client_request_store_id is True
    assert config.attr_fga_client_response_model_id is True
    assert config.attr_fga_client_user is False
    assert config.attr_http_client_request_duration is False
    assert config.attr_http_host is True
    assert config.attr_http_request_method is True
    assert config.attr_http_request_resend_count is True
    assert config.attr_http_response_status_code is True
    assert config.attr_http_server_request_duration is False
    assert config.attr_http_url_scheme is True
    assert config.attr_http_url_full is True
    assert config.attr_user_agent_original is True


def test_telemetry_metric_configuration_custom_initialization():
    config = TelemetryMetricConfiguration(
        enabled=False,
        attr_fga_client_request_client_id=False,
        attr_http_request_method=False,
    )

    # Assert custom initialization values
    assert config.enabled is False
    assert config.attr_fga_client_request_client_id is False
    assert config.attr_http_request_method is False
    # Check default values for other attributes
    assert config.attr_fga_client_request_method is True
    assert config.attr_http_host is True


def test_telemetry_metric_configuration_attributes_method():
    config = TelemetryMetricConfiguration(
        enabled=True,
        attr_fga_client_request_client_id=True,
        attr_http_request_method=False,
    )

    enabled_attributes = config.attributes()

    # Check only enabled attributes are returned
    assert (
        enabled_attributes[TelemetryAttributes.fga_client_request_client_id.name]
        is True
    )
    assert TelemetryAttributes.http_request_method.name not in enabled_attributes


def test_telemetry_metrics_configuration_default_initialization():
    metrics_config = TelemetryMetricsConfiguration()

    # Assert default metric configurations
    assert isinstance(
        metrics_config.counter_credentials_request, TelemetryMetricConfiguration
    )
    assert isinstance(
        metrics_config.histogram_request_duration, TelemetryMetricConfiguration
    )
    assert isinstance(
        metrics_config.histogram_query_duration, TelemetryMetricConfiguration
    )


def test_telemetry_metrics_configuration_custom_initialization():
    custom_config = TelemetryMetricConfiguration(enabled=False)
    metrics_config = TelemetryMetricsConfiguration(
        counter_credentials_request=custom_config
    )

    # Check that custom configuration is used
    assert metrics_config.counter_credentials_request is custom_config
    assert metrics_config.histogram_request_duration.enabled is True


def test_telemetry_metrics_configuration_setters():
    metrics_config = TelemetryMetricsConfiguration()

    new_config = TelemetryMetricConfiguration(enabled=False)
    metrics_config.counter_credentials_request = new_config

    assert metrics_config.counter_credentials_request is new_config


def test_telemetry_configuration_default_initialization():
    telemetry_config = TelemetryConfiguration()

    # Check the default metrics configuration is used
    assert isinstance(telemetry_config.metrics, TelemetryMetricsConfiguration)


def test_telemetry_configuration_custom_initialization():
    custom_metrics = TelemetryMetricsConfiguration()
    telemetry_config = TelemetryConfiguration(metrics=custom_metrics)

    assert telemetry_config.metrics is custom_metrics


def test_telemetry_configuration_setter():
    telemetry_config = TelemetryConfiguration()
    new_metrics = TelemetryMetricsConfiguration()
    telemetry_config.metrics = new_metrics

    assert telemetry_config.metrics is new_metrics
