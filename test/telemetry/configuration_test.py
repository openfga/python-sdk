from openfga_sdk.telemetry.attributes import TelemetryAttributes
from openfga_sdk.telemetry.configuration import (
    TelemetryConfiguration,
    TelemetryConfigurations,
    TelemetryMetricConfiguration,
    TelemetryMetricsConfiguration,
)
from openfga_sdk.telemetry.counters import TelemetryCounters
from openfga_sdk.telemetry.histograms import TelemetryHistograms


def test_telemetry_metric_configuration_default_initialization():
    config = TelemetryMetricConfiguration()

    assert config.fga_client_request_batch_check_size is False
    assert config.fga_client_request_client_id is False
    assert config.fga_client_request_method is False
    assert config.fga_client_request_model_id is False
    assert config.fga_client_request_store_id is False
    assert config.fga_client_response_model_id is False
    assert config.fga_client_user is False
    assert config.http_client_request_duration is False
    assert config.http_host is False
    assert config.http_request_method is False
    assert config.http_request_resend_count is False
    assert config.http_response_status_code is False
    assert config.http_server_request_duration is False
    assert config.url_scheme is False
    assert config.url_full is False
    assert config.user_agent_original is False


def test_telemetry_metric_configuration_custom_initialization():
    config = TelemetryMetricConfiguration(
        fga_client_request_client_id=False,
        http_request_method=True,
    )

    assert config.fga_client_request_client_id is False
    assert config.http_request_method is True
    assert config.fga_client_request_method is False
    assert config.user_agent_original is False


def test_telemetry_metric_configuration_custom_dict_object_keys_initialization():
    config = TelemetryMetricConfiguration(
        {
            "fga-client.request.client_id": False,
            "http.request.method": True,
        }
    )

    assert config.fga_client_request_client_id is False
    assert config.http_request_method is True
    assert config.fga_client_request_method is False
    assert config.user_agent_original is False
    assert config.fga_client_response_model_id is False


def test_telemetry_metric_configuration_custom_dict_string_keys_initialization():
    config = TelemetryMetricConfiguration(
        {
            TelemetryAttributes.fga_client_request_client_id: False,
            TelemetryAttributes.http_request_method: True,
        }
    )

    assert config.fga_client_request_client_id is False
    assert config.http_request_method is True
    assert config.fga_client_request_method is False
    assert config.user_agent_original is False
    assert config.fga_client_response_model_id is False


def test_telemetry_metric_configuration_custom_mixed_initialization():
    config = TelemetryMetricConfiguration(
        {
            TelemetryAttributes.fga_client_request_client_id: False,
            "http.request.method": True,
        },
        fga_client_response_model_id=True,
    )

    assert config.fga_client_request_client_id is False
    assert config.http_request_method is True
    assert config.fga_client_request_method is False
    assert config.user_agent_original is False
    assert config.fga_client_response_model_id is True


def test_telemetry_metric_configuration_custom_overwritten_initialization():
    config = TelemetryMetricConfiguration(
        {
            TelemetryAttributes.fga_client_request_client_id: True,
        },
        fga_client_request_client_id=False,
    )

    assert config.fga_client_request_client_id is False


def test_telemetry_metric_configuration_attributes_method():
    config = TelemetryMetricConfiguration(
        fga_client_request_client_id=True,
        http_request_method=False,
    )

    enabled_attributes = config.getAttributes()

    assert len(enabled_attributes) == 1
    assert TelemetryAttributes.fga_client_request_client_id in enabled_attributes
    assert TelemetryAttributes.http_request_method not in enabled_attributes


def test_telemetry_metrics_configuration_default_initialization():
    metrics_config = TelemetryMetricsConfiguration()

    assert metrics_config.fga_client_credentials_request is None
    assert metrics_config.fga_client_query_duration is None
    assert metrics_config.fga_client_request_duration is None


def test_telemetry_metrics_configuration_custom_initialization():
    custom_config = TelemetryMetricConfiguration()
    metrics_config = TelemetryMetricsConfiguration(
        fga_client_credentials_request=custom_config
    )

    assert metrics_config.fga_client_credentials_request is custom_config
    assert metrics_config.fga_client_request_duration is None
    assert metrics_config.fga_client_query_duration is None


def test_telemetry_metrics_configuration_custom_dict_object_keys_initialization():
    custom_config = TelemetryMetricConfiguration()
    metrics_config = TelemetryMetricsConfiguration(
        {TelemetryHistograms.fga_client_query_duration: custom_config}
    )

    assert metrics_config.fga_client_credentials_request is None
    assert metrics_config.fga_client_request_duration is None
    assert metrics_config.fga_client_query_duration is custom_config


def test_telemetry_metrics_configuration_custom_dict_string_keys_initialization():
    custom_config = TelemetryMetricConfiguration()
    metrics_config = TelemetryMetricsConfiguration(
        {"fga-client.request.duration": custom_config}
    )

    assert metrics_config.fga_client_credentials_request is None
    assert metrics_config.fga_client_request_duration is custom_config
    assert metrics_config.fga_client_query_duration is None


def test_telemetry_metrics_configuration_custom_mixed_initialization():
    custom_config = TelemetryMetricConfiguration()
    metrics_config = TelemetryMetricsConfiguration(
        {
            TelemetryHistograms.fga_client_query_duration: custom_config,
            "fga-client.request.duration": custom_config,
        },
        fga_client_credentials_request=custom_config,
    )

    assert metrics_config.fga_client_credentials_request is custom_config
    assert metrics_config.fga_client_request_duration is custom_config
    assert metrics_config.fga_client_query_duration is custom_config


def test_telemetry_metrics_configuration_custom_overwritten_initialization():
    custom_config = TelemetryMetricConfiguration()
    metrics_config = TelemetryMetricsConfiguration(
        {
            TelemetryHistograms.fga_client_query_duration: None,
        },
        fga_client_query_duration=custom_config,
    )

    assert metrics_config.fga_client_query_duration is custom_config


def test_telemetry_metrics_configuration_setters():
    metrics_config = TelemetryMetricsConfiguration()

    new_config = TelemetryMetricConfiguration()
    metrics_config.fga_client_credentials_request = new_config

    assert metrics_config.fga_client_credentials_request is new_config


def test_telemetry_configuration_default_initialization():
    telemetry_config = TelemetryConfiguration()

    assert telemetry_config.metrics is None


def test_telemetry_configuration_custom_initialization():
    custom_metrics = TelemetryMetricsConfiguration()
    telemetry_config = TelemetryConfiguration(metrics=custom_metrics)

    assert telemetry_config.metrics is custom_metrics


def test_telemetry_configuration_custom_dict_object_keys_initialization():
    custom_metrics = TelemetryMetricsConfiguration()
    telemetry_config = TelemetryConfiguration(
        {TelemetryConfigurations.metrics: custom_metrics}
    )

    assert telemetry_config.metrics is custom_metrics


def test_telemetry_configuration_custom_dict_string_keys_initialization():
    custom_metrics = TelemetryMetricsConfiguration()
    telemetry_config = TelemetryConfiguration({"metrics": custom_metrics})

    assert telemetry_config.metrics is custom_metrics


def test_telemetry_configuration_custom_overwritten_initialization():
    custom_metrics = TelemetryMetricsConfiguration()
    telemetry_config = TelemetryConfiguration(
        {TelemetryConfigurations.metrics: None}, metrics=custom_metrics
    )

    assert telemetry_config.metrics is custom_metrics


def test_telemetry_configuration_custom_full_initialization():
    telemetry_config = TelemetryConfiguration(
        {
            "metrics": {
                "fga-client.credentials.request": {
                    "fga-client.request.client_id": False,
                    "http.request.method": True,
                },
                "fga-client.request.duration": {
                    "fga-client.request.client_id": True,
                    "http.request.method": False,
                },
            }
        }
    )

    assert (
        telemetry_config.metrics.fga_client_credentials_request.fga_client_request_client_id
        is False
    )
    assert (
        telemetry_config.metrics.fga_client_credentials_request.http_request_method
        is True
    )
    assert (
        telemetry_config.metrics.fga_client_request_duration.fga_client_request_client_id
        is True
    )
    assert (
        telemetry_config.metrics.fga_client_request_duration.http_request_method
        is False
    )


def test_telemetry_configuration_setter():
    telemetry_config = TelemetryConfiguration()
    new_metrics = TelemetryMetricsConfiguration()
    telemetry_config.metrics = new_metrics

    assert telemetry_config.metrics is new_metrics


def test_default_telemetry_configuration():
    config = TelemetryConfiguration.getSdkDefaults()

    assert isinstance(config, dict)
    assert len(config) == 1

    assert TelemetryConfigurations.metrics in config


def test_default_telemetry_metrics_configuration():
    metrics_config = TelemetryMetricsConfiguration.getSdkDefaults()

    assert isinstance(metrics_config, dict)
    assert len(metrics_config) == 3

    assert TelemetryCounters.fga_client_credentials_request in metrics_config
    assert TelemetryHistograms.fga_client_query_duration in metrics_config
    assert TelemetryHistograms.fga_client_request_duration in metrics_config


def test_default_telemetry_metric_configuration():
    metric_config = TelemetryMetricConfiguration.getSdkDefaults()

    assert isinstance(metric_config, dict)
    assert len(metric_config) == 16

    assert (
        metric_config[TelemetryAttributes.fga_client_request_batch_check_size] is False
    )
    assert metric_config[TelemetryAttributes.fga_client_request_client_id] is True
    assert metric_config[TelemetryAttributes.fga_client_request_method] is True
    assert metric_config[TelemetryAttributes.fga_client_request_model_id] is True
    assert metric_config[TelemetryAttributes.fga_client_request_store_id] is True
    assert metric_config[TelemetryAttributes.fga_client_response_model_id] is True
    assert metric_config[TelemetryAttributes.fga_client_user] is False
    assert metric_config[TelemetryAttributes.http_client_request_duration] is False
    assert metric_config[TelemetryAttributes.http_host] is True
    assert metric_config[TelemetryAttributes.http_request_method] is True
    assert metric_config[TelemetryAttributes.http_request_resend_count] is True
    assert metric_config[TelemetryAttributes.http_response_status_code] is True
    assert metric_config[TelemetryAttributes.http_server_request_duration] is False
    assert metric_config[TelemetryAttributes.url_scheme] is True
    assert metric_config[TelemetryAttributes.url_full] is True
    assert metric_config[TelemetryAttributes.user_agent_original] is True
