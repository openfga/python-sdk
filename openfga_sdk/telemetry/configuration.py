from typing import NamedTuple, Optional

from openfga_sdk.telemetry.attributes import TelemetryAttribute, TelemetryAttributes
from openfga_sdk.telemetry.counters import TelemetryCounter, TelemetryCounters
from openfga_sdk.telemetry.histograms import TelemetryHistogram, TelemetryHistograms


class TelemetryMetricConfiguration:
    """
    Telemetry configuration for an individual histogram or counter. When instantiated directly, all attributes are disabled by default.
    Use the `getDefaultTelemetryMetricConfiguration` method to get an instance of TelemetryMetricConfiguration pre-configured with reasonable defaults enabled.
    """

    _state: dict[TelemetryAttribute, bool] = {}
    _valid: bool | None = None

    def __init__(
        self,
        config: Optional[dict[TelemetryAttribute, bool]] = None,
        fga_client_request_client_id: Optional[bool] = None,
        fga_client_request_method: Optional[bool] = None,
        fga_client_request_model_id: Optional[bool] = None,
        fga_client_request_store_id: Optional[bool] = None,
        fga_client_response_model_id: Optional[bool] = None,
        fga_client_user: Optional[bool] = None,
        http_client_request_duration: Optional[bool] = None,
        http_host: Optional[bool] = None,
        http_request_method: Optional[bool] = None,
        http_request_resend_count: Optional[bool] = None,
        http_response_status_code: Optional[bool] = None,
        http_server_request_duration: Optional[bool] = None,
        url_scheme: Optional[bool] = None,
        url_full: Optional[bool] = None,
        user_agent_original: Optional[bool] = None,
    ):
        """
        Initialize a new instance of the `TelemetryMetricConfiguration` class.

        :param config: A dictionary containing the configuration for the telemetry metrics.
        :param fga_client_request_client_id: The `fga-client.request.client_id` attribute includes the client ID associated with the request, if any.
        :param fga_client_request_method: The `fga-client.request.method` attribute includes the FGA method/action that was performed.
        :param fga_client_request_model_id: The `fga-client.request.model_id` attribute includes the authorization model ID that was sent as part of the request, if any.
        :param fga_client_request_store_id: The `fga-client.request.store_id` attribute includes the store ID that was sent as part of the request, if any.
        :param fga_client_response_model_id: The `fga-client.response.model_id` attribute includes the authorization model ID that the FGA server used.
        :param fga_client_user: The `fga-client.user` attribute includes the user associated with the request, if any.
        :param http_client_request_duration: The `http.client.request.duration` attribute includes the duration of the request from the client's perspective.
        :param http_host: The `http.host` attribute includes the host name of the request.
        :param http_request_method: The `http.request.method` attribute includes the HTTP method of the request.
        :param http_request_resend_count: The `http.request.resend_count` attribute includes the number of times the request was resent.
        :param http_response_status_code: The `http.response.status_code` attribute includes the HTTP status code of the response.
        :param http_server_request_duration: The `http.server.request.duration` attribute includes the duration of the request from the server's perspective.
        :param url_scheme: The `url.scheme` attribute includes the scheme of the request URL.
        :param url_full: The `url.full` attribute includes the full URL of the request.
        :param user_agent_original: The `user_agent.original` attribute includes the original user agent string of the request.
        """

        self.configure(
            config=config,
            clear=True,
        )

        if fga_client_request_client_id is not None:
            self._state[TelemetryAttributes.fga_client_request_client_id] = (
                fga_client_request_client_id
            )

        if fga_client_request_method is not None:
            self._state[TelemetryAttributes.fga_client_request_method] = (
                fga_client_request_method
            )

        if fga_client_request_model_id is not None:
            self._state[TelemetryAttributes.fga_client_request_model_id] = (
                fga_client_request_model_id
            )

        if fga_client_request_store_id is not None:
            self._state[TelemetryAttributes.fga_client_request_store_id] = (
                fga_client_request_store_id
            )

        if fga_client_response_model_id is not None:
            self._state[TelemetryAttributes.fga_client_response_model_id] = (
                fga_client_response_model_id
            )

        if fga_client_user is not None:
            self._state[TelemetryAttributes.fga_client_user] = fga_client_user

        if http_client_request_duration is not None:
            self._state[TelemetryAttributes.http_client_request_duration] = (
                http_client_request_duration
            )

        if http_host is not None:
            self._state[TelemetryAttributes.http_host] = http_host

        if http_request_method is not None:
            self._state[TelemetryAttributes.http_request_method] = http_request_method

        if http_request_resend_count is not None:
            self._state[TelemetryAttributes.http_request_resend_count] = (
                http_request_resend_count
            )

        if http_response_status_code is not None:
            self._state[TelemetryAttributes.http_response_status_code] = (
                http_response_status_code
            )

        if http_server_request_duration is not None:
            self._state[TelemetryAttributes.http_server_request_duration] = (
                http_server_request_duration
            )

        if url_scheme is not None:
            self._state[TelemetryAttributes.url_scheme] = url_scheme

        if url_full is not None:
            self._state[TelemetryAttributes.url_full] = url_full

        if user_agent_original is not None:
            self._state[TelemetryAttributes.user_agent_original] = user_agent_original

        self._valid = None  # Reset the validation state

    @property
    def fga_client_request_client_id(self) -> bool:
        """
        Get the configuration for the `fga-client.request.client_id` attribute.

        :return: The configuration for the `fga-client.request.client_id` attribute.
        """

        return self._state[TelemetryAttributes.fga_client_request_client_id]

    @fga_client_request_client_id.setter
    def fga_client_request_client_id(self, value: bool):
        """
        Set the configuration for the `fga-client.request.client_id` attribute.

        :param value: The configuration for the `fga-client.request.client_id` attribute.
        """

        self._valid = None  # Reset the validation state
        self._state[TelemetryAttributes.fga_client_request_client_id] = value

    @property
    def fga_client_request_method(self) -> bool:
        """
        Get the configuration for the `fga-client.request.method` attribute.

        :return: The configuration for the `fga-client.request.method` attribute.
        """

        return self._state[TelemetryAttributes.fga_client_request_method]

    @fga_client_request_method.setter
    def fga_client_request_method(self, value: bool):
        """
        Set the configuration for the `fga-client.request.method` attribute.

        :param value: The configuration for the `fga-client.request.method` attribute.
        """

        self._valid = None  # Reset the validation state
        self._state[TelemetryAttributes.fga_client_request_method] = value

    @property
    def fga_client_request_model_id(self) -> bool:
        """
        Get the configuration for the `fga-client.request.model_id` attribute.

        :return: The configuration for the `fga-client.request.model_id` attribute.
        """

        return self._state[TelemetryAttributes.fga_client_request_model_id]

    @fga_client_request_model_id.setter
    def fga_client_request_model_id(self, value: bool):
        """
        Set the configuration for the `fga-client.request.model_id` attribute.

        :param value: The configuration for the `fga-client.request.model_id` attribute.
        """

        self._valid = None  # Reset the validation state
        self._state[TelemetryAttributes.fga_client_request_model_id] = value

    @property
    def fga_client_request_store_id(self) -> bool:
        """
        Get the configuration for the `fga-client.request.store_id` attribute.

        :return: The configuration for the `fga-client.request.store_id` attribute.
        """

        return self._state[TelemetryAttributes.fga_client_request_store_id]

    @fga_client_request_store_id.setter
    def fga_client_request_store_id(self, value: bool):
        """
        Set the configuration for the `fga-client.request.store_id` attribute.

        :param value: The configuration for the `fga-client.request.store_id` attribute.
        """

        self._valid = None  # Reset the validation state
        self._state[TelemetryAttributes.fga_client_request_store_id] = value

    @property
    def fga_client_response_model_id(self) -> bool:
        """
        Get the configuration for the `fga-client.response.model_id` attribute.

        :return: The configuration for the `fga-client.response.model_id` attribute.
        """

        return self._state[TelemetryAttributes.fga_client_response_model_id]

    @fga_client_response_model_id.setter
    def fga_client_response_model_id(self, value: bool):
        """
        Set the configuration for the `fga-client.response.model_id` attribute.

        :param value: The configuration for the `fga-client.response.model_id` attribute.
        """

        self._valid = None  # Reset the validation state
        self._state[TelemetryAttributes.fga_client_response_model_id] = value

    @property
    def fga_client_user(self) -> bool:
        """
        Get the configuration for the `fga-client.user` attribute.

        :return: The configuration for the `fga-client.user` attribute.
        """

        return self._state[TelemetryAttributes.fga_client_user]

    @fga_client_user.setter
    def fga_client_user(self, value: bool):
        """
        Set the configuration for the `fga-client.user` attribute.

        :param value: The configuration for the `fga-client.user` attribute.
        """

        self._valid = None  # Reset the validation state
        self._state[TelemetryAttributes.fga_client_user] = value

    @property
    def http_client_request_duration(self) -> bool:
        """
        Get the configuration for the `http.client.request.duration` attribute.

        :return: The configuration for the `http.client.request.duration` attribute.
        """

        return self._state[TelemetryAttributes.http_client_request_duration]

    @http_client_request_duration.setter
    def http_client_request_duration(self, value: bool):
        """
        Set the configuration for the `http.client.request.duration` attribute.

        :param value: The configuration for the `http.client.request.duration` attribute.
        """

        self._valid = None  # Reset the validation state
        self._state[TelemetryAttributes.http_client_request_duration] = value

    @property
    def http_host(self) -> bool:
        """
        Get the configuration for the `http.host` attribute.

        :return: The configuration for the `http.host` attribute.
        """

        return self._state[TelemetryAttributes.http_host]

    @http_host.setter
    def http_host(self, value: bool):
        """
        Set the configuration for the `http.host` attribute.

        :param value: The configuration for the `http.host` attribute.
        """

        self._valid = None  # Reset the validation state
        self._state[TelemetryAttributes.http_host] = value

    @property
    def http_request_method(self) -> bool:
        """
        Get the configuration for the `http.request.method` attribute.

        :return: The configuration for the `http.request.method` attribute.
        """

        return self._state[TelemetryAttributes.http_request_method]

    @http_request_method.setter
    def http_request_method(self, value: bool):
        """
        Set the configuration for the `http.request.method` attribute.

        :param value: The configuration for the `http.request.method` attribute.
        """

        self._valid = None  # Reset the validation state
        self._http_request_method = value

    @property
    def http_request_resend_count(self) -> bool:
        """
        Get the configuration for the `http.request.resend_count` attribute.

        :return: The configuration for the `http.request.resend_count` attribute.
        """

        return self._state[TelemetryAttributes.http_request_resend_count]

    @http_request_resend_count.setter
    def http_request_resend_count(self, value: bool):
        """
        Set the configuration for the `http.request.resend_count` attribute.

        :param value: The configuration for the `http.request.resend_count` attribute.
        """

        self._valid = None  # Reset the validation state
        self._state[TelemetryAttributes.http_request_resend_count] = value

    @property
    def http_response_status_code(self) -> bool:
        """
        Get the configuration for the `http.response.status_code` attribute.

        :return: The configuration for the `http.response.status_code` attribute.
        """

        return self._state[TelemetryAttributes.http_response_status_code]

    @http_response_status_code.setter
    def http_response_status_code(self, value: bool):
        """
        Set the configuration for the `http.response.status_code` attribute.

        :param value: The configuration for the `http.response.status_code` attribute.
        """

        self._valid = None  # Reset the validation state
        self._state[TelemetryAttributes.http_response_status_code] = value

    @property
    def http_server_request_duration(self) -> bool:
        """
        Get the configuration for the `http.server.request.duration` attribute.

        :return: The configuration for the `http.server.request.duration` attribute.
        """

        return self._state[TelemetryAttributes.http_server_request_duration]

    @http_server_request_duration.setter
    def http_server_request_duration(self, value: bool):
        """
        Set the configuration for the `http.server.request.duration` attribute.

        :param value: The configuration for the `http.server.request.duration` attribute.
        """

        self._valid = None  # Reset the validation state
        self._state[TelemetryAttributes.http_server_request_duration] = value

    @property
    def url_scheme(self) -> bool:
        """
        Get the configuration for the `url.scheme` attribute.

        :return: The configuration for the `url.scheme` attribute.
        """

        return self._state[TelemetryAttributes.url_scheme]

    @url_scheme.setter
    def url_scheme(self, value: bool):
        """
        Set the configuration for the `url.scheme` attribute.

        :param value: The configuration for the `url.scheme` attribute.
        """

        self._valid = None  # Reset the validation state
        self._state[TelemetryAttributes.url_scheme] = value

    @property
    def url_full(self) -> bool:
        """
        Get the configuration for the `url.full` attribute.

        :return: The configuration for the `url.full` attribute.
        """

        return self._state[TelemetryAttributes.url_full]

    @url_full.setter
    def url_full(self, value: bool):
        """
        Set the configuration for the `url.full` attribute.

        :param value: The configuration for the `url.full` attribute.
        """

        self._valid = None  # Reset the validation state
        self._state[TelemetryAttributes.url_full] = value

    @property
    def user_agent_original(self) -> bool:
        """
        Get the configuration for the `user_agent.original` attribute.

        :return: The configuration for the `user_agent.original` attribute.
        """

        return self._state[TelemetryAttributes.user_agent_original]

    @user_agent_original.setter
    def user_agent_original(self, value: bool):
        """
        Set the configuration for the `user_agent.original` attribute.

        :param value: The configuration for the `user_agent.original` attribute.
        """

        self._valid = None  # Reset the validation state
        self._state[TelemetryAttributes.user_agent_original] = value

    def clear(self) -> None:
        """
        Reset the configuration to the default state (all attributes disabled).
        """

        # Reset the configuration to the default state
        self._state = {
            TelemetryAttributes.fga_client_request_client_id: False,
            TelemetryAttributes.fga_client_request_method: False,
            TelemetryAttributes.fga_client_request_model_id: False,
            TelemetryAttributes.fga_client_request_store_id: False,
            TelemetryAttributes.fga_client_response_model_id: False,
            TelemetryAttributes.fga_client_user: False,
            TelemetryAttributes.http_client_request_duration: False,
            TelemetryAttributes.http_host: False,
            TelemetryAttributes.http_request_method: False,
            TelemetryAttributes.http_request_resend_count: False,
            TelemetryAttributes.http_response_status_code: False,
            TelemetryAttributes.http_server_request_duration: False,
            TelemetryAttributes.url_scheme: False,
            TelemetryAttributes.url_full: False,
            TelemetryAttributes.user_agent_original: False,
        }

        # Reset the validation state
        self._valid = True

    def configure(
        self,
        config: Optional[dict[TelemetryAttribute | str, bool]] = None,
        clear: Optional[bool] = False,
    ) -> None:
        """
        Configure the telemetry metric.
        """

        # Reset the configuration to the default state
        if clear is True:
            self.clear()

        # Apply an incoming configuration, if provided
        if isinstance(config, dict):
            for attribute, enabled in config.items():
                if isinstance(attribute, str):
                    attribute = TelemetryAttributes.get(name=attribute)

                if not isinstance(attribute, TelemetryAttribute):
                    raise ValueError(
                        f"Invalid attribute type provided in `TelemetryMetricConfiguration`; `TelemetryAttribute` expected, but `{type(attribute)}` was provided.",
                        attribute,
                    )

                if not isinstance(enabled, bool):
                    raise ValueError(
                        f"Invalid attribute value provided in `TelemetryMetricConfiguration`; `bool` expected, but `{type(enabled)}` was provided.",
                        attribute,
                    )

                if attribute not in self._state:
                    raise ValueError(
                        f"Invalid attribute provided in `TelemetryMetricConfiguration`; `{attribute.name}` is not a supported attribute type for this context.",
                        attribute,
                    )

                self._state[attribute] = enabled

            # Reset the validation state
            self._valid = None

    def getAttributes(
        self, filter_enabled: Optional[bool] = True
    ) -> dict[TelemetryAttribute, bool]:
        """
        Returns a list of supported attributes. If `filter_enabled` is `True`, only enabled attributes are returned.

        :param filter_enabled: A boolean indicating whether to filter the list to only include enabled attributes.

        :return: A list of enabled attributes.
        """

        attributes = self._state

        if filter_enabled is True:
            return [
                attribute
                for attribute, enabled in attributes.items()
                if enabled is True
            ]

        return attributes

    def isEnabled(self, attribute: Optional[TelemetryAttribute] = None) -> bool:
        """
        Check if this metric is enabled for telemetry, based on whether any attributes are enabled.

        :return: A boolean indicating whether any attributes are enabled for the metric.
        """

        # If no attribute is specified, check if any attributes are enabled
        if attribute is None:
            return True if any(self.getAttributes(filter_enabled=True)) else False

        # Check if the specified attribute is enabled
        if attribute in self._state:
            return self._state[attribute]

        return False

    def isValid(self, raise_exception: Optional[bool] = False) -> bool:
        """
        Validate the telemetry metric configuration.

        :param raise_exception: A boolean indicating whether to raise an exception if the configuration is invalid.

        :return: A boolean indicating whether the metric configuration is valid.
        """

        # Check if the validation state is already cached
        if self._valid is not None:
            return self._valid

        # Validate the configuration
        self._valid = all([isinstance(value, bool) for value in self._state.values()])

        # If requested, raise an exception if the configuration is invalid
        if self._valid is False and raise_exception is True:
            raise ValueError("Invalid TelemetryMetricConfiguration.")

        # Return the validation state
        return self._valid

    @staticmethod
    def getSdkDefaults() -> dict[TelemetryAttribute, bool]:
        """
        Get the default SDK configuration for the telemetry metric.

        :return: The default SDK configuration for the telemetry metric.
        """
        return {
            TelemetryAttributes.fga_client_request_client_id: True,
            TelemetryAttributes.fga_client_request_method: True,
            TelemetryAttributes.fga_client_request_model_id: True,
            TelemetryAttributes.fga_client_request_store_id: True,
            TelemetryAttributes.fga_client_response_model_id: True,
            TelemetryAttributes.fga_client_user: False,
            TelemetryAttributes.http_client_request_duration: False,
            TelemetryAttributes.http_host: True,
            TelemetryAttributes.http_request_method: True,
            TelemetryAttributes.http_request_resend_count: True,
            TelemetryAttributes.http_response_status_code: True,
            TelemetryAttributes.http_server_request_duration: False,
            TelemetryAttributes.url_scheme: True,
            TelemetryAttributes.url_full: True,
            TelemetryAttributes.user_agent_original: True,
        }


class TelemetryMetricsConfiguration:
    _state: dict[
        TelemetryHistogram | TelemetryCounter, TelemetryMetricConfiguration | None
    ] = {}
    _valid: bool | None = None

    def __init__(
        self,
        config: Optional[
            dict[
                TelemetryHistogram | TelemetryCounter,
                TelemetryMetricConfiguration | None,
            ]
        ] = None,
        fga_client_credentials_request: Optional[TelemetryMetricConfiguration] = None,
        fga_client_request_duration: Optional[TelemetryMetricConfiguration] = None,
        fga_client_query_duration: Optional[TelemetryMetricConfiguration] = None,
        fga_client_request: Optional[TelemetryMetricConfiguration] = None,
    ):
        """
        Initialize a new instance of the `TelemetryMetricsConfiguration` class.

        :param config: A dictionary containing the configuration for the telemetry metrics.
        :param fga_client_credentials_request: The `fga-client.credentials.request` counter collects the number of times a new token is requested using ClientCredentials.
        :param fga_client_request_duration: The `fga-client.query.duration` histogram tracks how long requests take to complete from the client's perspective.
        :param fga_client_query_duration: The `fga-client.request.duration` histogram tracks how long requests take to process from the server's perspective.
        :param fga_client_request: The `fga-client.request` counter collects the number of requests made to the FGA server.
        """

        # Instantiate with default state, and apply the incoming configuration, if one was provided
        self.configure(config=config, clear=True)

        if fga_client_credentials_request is not None:
            self._state[TelemetryCounters.fga_client_credentials_request] = (
                fga_client_credentials_request
            )

        if fga_client_request_duration is not None:
            self._state[TelemetryHistograms.fga_client_request_duration] = (
                fga_client_request_duration
            )

        if fga_client_query_duration is not None:
            self._state[TelemetryHistograms.fga_client_query_duration] = (
                fga_client_query_duration
            )

        if fga_client_request is not None:
            self._state[TelemetryCounters.fga_client_request] = fga_client_request

        # Reset the validation state
        self._valid = None

    @property
    def fga_client_request(self) -> TelemetryMetricConfiguration | None:
        """
        Get the configuration for the `fga-client.request` counter.

        :return: The configuration for the `fga-client.request` counter.
        """

        return self._state[TelemetryCounters.fga_client_request]

    @fga_client_request.setter
    def fga_client_request(self, value: TelemetryMetricConfiguration | None):
        """
        Set the configuration for the `fga-client.request` counter.

        :param value: The configuration for the `fga-client.request` counter.
        """

        self._valid = None  # Reset the validation state
        self._state[TelemetryCounters.fga_client_request] = value

    @property
    def fga_client_credentials_request(self) -> TelemetryMetricConfiguration | None:
        """
        Get the configuration for the `fga-client.credentials.request` counter.

        :return: The configuration for the `fga-client.credentials.request` counter.
        """

        return self._state[TelemetryCounters.fga_client_credentials_request]

    @fga_client_credentials_request.setter
    def fga_client_credentials_request(
        self, value: TelemetryMetricConfiguration | None
    ):
        """
        Set the configuration for the `fga-client.credentials.request` counter.

        :param value: The configuration for the `fga-client.credentials.request` counter.
        """

        self._valid = None  # Reset the validation state
        self._state[TelemetryCounters.fga_client_credentials_request] = value

    @property
    def fga_client_request_duration(self) -> TelemetryMetricConfiguration | None:
        """
        Get the configuration for the `fga-client.query.duration` histogram.

        :return: The configuration for the `fga-client.query.duration` histogram.
        """

        return self._state[TelemetryHistograms.fga_client_request_duration]

    @fga_client_request_duration.setter
    def fga_client_request_duration(self, value: TelemetryMetricConfiguration | None):
        """
        Set the configuration for the `fga-client.query.duration` histogram.

        :param value: The configuration for the `fga-client.query.duration` histogram.
        """

        self._valid = None  # Reset the validation state
        self._state[TelemetryHistograms.fga_client_request_duration] = value

    @property
    def fga_client_query_duration(self) -> TelemetryMetricConfiguration | None:
        """
        Get the configuration for the `fga-client.request.duration` histogram.

        :return: The configuration for the `fga-client.request.duration` histogram.
        """

        return self._state[TelemetryHistograms.fga_client_query_duration]

    @fga_client_query_duration.setter
    def fga_client_query_duration(self, value: TelemetryMetricConfiguration | None):
        """
        Set the configuration for the `fga-client.request.duration` histogram.

        :param value: The configuration for the `fga-client.request.duration` histogram.
        """

        self._valid = None  # Reset the validation state
        self._state[TelemetryHistograms.fga_client_query_duration] = value

    def clear(self) -> None:
        """
        Reset the configuration to the default state (all attributes disabled).
        """
        self._state = {
            TelemetryCounters.fga_client_request: None,
            TelemetryCounters.fga_client_credentials_request: None,
            TelemetryHistograms.fga_client_request_duration: None,
            TelemetryHistograms.fga_client_query_duration: None,
        }
        self._valid = True

    def configure(
        self,
        config: Optional[
            dict[
                TelemetryHistogram | TelemetryCounter | str,
                TelemetryMetricConfiguration | dict[TelemetryAttribute, bool] | None,
            ]
        ] = None,
        clear: Optional[bool] = False,
    ) -> None:
        """
        Configure metrics reporting for telemetry.
        """
        if clear is True:
            self.clear()

        if isinstance(config, dict):
            for metric, configuration in config.items():
                if isinstance(metric, str):
                    metric = TelemetryCounters.get(
                        name=metric
                    ) or TelemetryHistograms.get(name=metric)

                if not isinstance(metric, TelemetryCounter) and not isinstance(
                    metric, TelemetryHistogram
                ):
                    raise ValueError(
                        f"Invalid metric type provided in `TelemetryMetricsConfiguration`; `TelemetryHistogram` or `TelemetryCounter` was expected, but `{type(metric)}` was provided.",
                        metric,
                    )

                if isinstance(configuration, dict):
                    configuration = TelemetryMetricConfiguration(configuration)

                if (
                    not isinstance(configuration, TelemetryMetricConfiguration)
                    and configuration is not None
                ):
                    raise ValueError(
                        f"Invalid metric configuration type provided in `TelemetryMetricsConfiguration`; `TelemetryMetricConfiguration` or `None` was expected, but `{type(configuration)}` was provided.",
                        configuration,
                    )

                if metric not in self._state:
                    raise ValueError(
                        f"Invalid metric provided in `TelemetryMetricsConfiguration`; `{metric.name}` is not a supported metric type for this context.",
                        metric,
                    )

                self._state[metric] = configuration

        self._valid = None

    def getMetrics(
        self, filter_enabled: Optional[bool] = True
    ) -> dict[
        TelemetryHistogram | TelemetryCounter, TelemetryMetricConfiguration | None
    ]:
        """
        Returns a list of supported metrics. If `filter_enabled` is `True`, only enabled metrics are returned.

        :param filter_enabled: A boolean indicating whether to filter the list to only include enabled metrics.

        :return: A list of enabled metrics.
        """

        metrics = self._state

        if filter_enabled is True:
            return [
                metric
                for metric, configuration in metrics.items()
                if configuration is not None and configuration.isEnabled()
            ]

        return metrics

    def isEnabled(
        self, metric: Optional[TelemetryCounter | TelemetryHistogram] = None
    ) -> bool:
        """
        Check if a metric is enabled for telemetry.

        :return: A boolean indicating whether any metric is enabled.
        """

        # If no metric is specified, check if any metrics are enabled
        if metric is None:
            return True if any(self.getMetrics(filter_enabled=True)) else False

        # Check if the specified metric is enabled
        if metric in self._state:
            if (
                self._state[metric] is not None
                and self._state[metric].isEnabled() is True
            ):
                return True

        return False

    def isValid(self, raise_exception: Optional[bool] = False) -> bool:
        """
        Validate the telemetry metrics configuration.

        :param raise_exception: A boolean indicating whether to raise an exception if the configuration is invalid.

        :return: A boolean indicating whether the metrics configuration is valid, including all sub-configurations.
        """

        # Check if the validation state is already cached
        if self._valid is not None:
            return self._valid

        enabled = self.getMetrics(filter_enabled=True)

        # Validate all sub-configurations and cache the result
        self._valid = [configuration.isValid() for configuration in enabled.values()]

        # If requested, raise an exception if the configuration is invalid
        if self._valid is False and raise_exception is True:
            raise ValueError("Invalid TelemetryMetricsConfiguration.")

        # Return the validation state
        return self._valid

    @staticmethod
    def getSdkDefaults() -> (
        dict[TelemetryHistogram | TelemetryCounter, TelemetryMetricConfiguration | None]
    ):
        """
        Get the default SDK configuration for telemetry metrics.

        :return: The default SDK configuration for telemetry metrics.
        """
        return {
            TelemetryCounters.fga_client_credentials_request: TelemetryMetricConfiguration.getSdkDefaults(),
            TelemetryHistograms.fga_client_query_duration: TelemetryMetricConfiguration.getSdkDefaults(),
            TelemetryHistograms.fga_client_request_duration: TelemetryMetricConfiguration.getSdkDefaults(),
        }


class TelemetryConfigurationType(NamedTuple):
    name: str
    configurationClass: object


class TelemetryConfigurations:
    metrics: TelemetryConfigurationType = TelemetryConfigurationType(
        name="metrics",
        configurationClass=TelemetryMetricsConfiguration,
    )

    _configurations: list[TelemetryConfigurationType] = [metrics]

    @staticmethod
    def get(
        name: Optional[str] = None,
    ) -> list[TelemetryConfigurationType] | TelemetryConfigurationType | None:
        if name is None:
            return TelemetryConfigurations._configurations

        for configuration in TelemetryConfigurations._configurations:
            if configuration.name == name:
                return configuration

        return None


class TelemetryConfiguration:
    _state: dict[str, TelemetryMetricsConfiguration | None] = {}
    _valid: bool | None = None

    def __init__(
        self,
        config: Optional[dict[str, TelemetryMetricsConfiguration | None]] = None,
        metrics: Optional[TelemetryMetricsConfiguration] = None,
    ):
        """
        Initialize a new instance of the `TelemetryConfiguration` class.

        :param config: A dictionary containing the configuration for telemetry.
        :param metrics: Customize which metrics and attributes are included in telemetry collection.
        """

        # Instantiate with default state, and apply the incoming configuration, if one was provided
        self.configure(config=config, clear=True)

        if metrics is not None:
            self._state[TelemetryConfigurations.metrics] = metrics

    @property
    def metrics(self) -> TelemetryMetricsConfiguration | None:
        """
        Get the metrics configuration for telemetry.

        :return: The metrics configuration for telemetry.
        """

        return self._state[TelemetryConfigurations.metrics]

    @metrics.setter
    def metrics(self, value: TelemetryMetricsConfiguration | None):
        """
        Set the metrics configuration for telemetry.

        :param value: The metrics configuration for telemetry.
        """

        if value is not None and not isinstance(value, TelemetryMetricsConfiguration):
            raise ValueError(
                "A `metrics` configuration must be an instance of `TelemetryMetricsConfiguration` or `None`."
            )

        self._valid = None
        self._state[TelemetryConfigurations.metrics] = value

    def clear(self) -> None:
        """
        Reset the configuration to the default state (all attributes disabled).
        """
        self._state = {
            TelemetryConfigurations.metrics: None,
        }
        self._valid = True

    def configure(
        self,
        config: Optional[
            dict[
                TelemetryConfigurationType | str,
                TelemetryMetricsConfiguration
                | dict[
                    TelemetryHistogram | TelemetryCounter,
                    TelemetryMetricConfiguration
                    | dict[TelemetryAttribute, bool]
                    | None,
                ]
                | None,
            ]
        ] = None,
        clear: Optional[bool] = False,
    ) -> None:
        """
        Configure telemetry reporting.
        """
        if clear is True:
            self.clear()

        if isinstance(config, dict):
            for context, configuration in config.items():
                if isinstance(context, str):
                    context = TelemetryConfigurations.get(context)

                if not isinstance(context, TelemetryConfigurationType):
                    raise ValueError(
                        f"Invalid context provided in `TelemetryConfiguration`; a valid string or an `TelemetryConfigurationType` instance was expected, but `{type(context)}` was provided.",
                        context,
                    )

                if isinstance(configuration, dict):
                    configuration = TelemetryMetricsConfiguration(configuration)

                if (
                    not isinstance(configuration, context.configurationClass)
                    and configuration is not None
                ):
                    raise ValueError(
                        f"Invalid context configuration provided in `TelemetryConfiguration`; a {type(context.configurationClass)} was expected, but `{type(configuration)}` was provided.",
                        configuration,
                    )

                if context not in self._state:
                    raise ValueError(
                        f"Invalid context provided in `TelemetryConfiguration`; `{context.name}` is not a supported context type for this configuration context.",
                        context,
                    )

                self._state[context] = configuration

        self._valid = None

    def getConfigurations(
        self, filter_enabled: Optional[bool] = True
    ) -> dict[TelemetryConfigurationType, TelemetryMetricsConfiguration | None]:
        """
        Returns a list of supported reporting contexts. If `filter_enabled` is `True`, only enabled contexts are returned.

        :param filter_enabled: A boolean indicating whether to filter the list to only include enabled contexts.

        :return: A list of enabled contexts.
        """

        contexts = self._state

        if filter_enabled is True:
            return {
                context: configuration
                for context, configuration in contexts.items()
                if configuration is not None and configuration.isEnabled()
            }

        return contexts

    def isEnabled(
        self, configuration: Optional[TelemetryConfigurationType] = None
    ) -> bool:
        """
        Check if telemetry is enabled.

        :return: A boolean indicating whether telemetry is enabled.
        """

        if configuration is None:
            return True if any(self.getConfigurations(filter_enabled=True)) else False

        if configuration in self._state:
            if (
                self._state[configuration] is not None
                or self._state[configuration].isEnabled() is True
            ):
                return self._state[configuration].isEnabled()

        return False

    def isValid(self, raise_exception: Optional[bool] = False) -> bool:
        """
        Validate the telemetry configuration.

        :param raise_exception: A boolean indicating whether to raise an exception if the configuration is invalid.

        :return: A boolean indicating whether the telemetry configuration is valid, including all sub-configurations.
        """

        if self._valid is not None:
            return self._valid

        enabled = self.getConfigurations(filter_enabled=True)

        self._valid = all(
            [configuration.isValid() for configuration in enabled.values()]
        )

        if self._valid is False and raise_exception is True:
            raise ValueError("Invalid TelemetryConfiguration.")

        return self._valid

    @staticmethod
    def getSdkDefaults() -> (
        dict[TelemetryConfigurationType, TelemetryMetricsConfiguration | None]
    ):
        """
        Get the default SDK configuration for telemetry.

        :return: The default SDK configuration for telemetry.
        """
        return {
            TelemetryConfigurations.metrics: TelemetryMetricsConfiguration.getSdkDefaults(),
        }


def isMetricEnabled(
    config: TelemetryConfiguration | TelemetryMetricsConfiguration,
    metric: TelemetryCounter | TelemetryHistogram,
) -> bool:
    """
    Check if a particular metric is enabled for telemetry collection.
    """

    if config is not None and metric is not None:
        if isinstance(config, TelemetryConfiguration):
            config = config.metrics

        if isinstance(config, TelemetryMetricsConfiguration):
            return config.isEnabled(metric)

    return False
