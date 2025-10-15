from openfga_sdk.configuration import Configuration
from openfga_sdk.exceptions import FgaValidationException
from openfga_sdk.telemetry.attributes import TelemetryAttribute
from openfga_sdk.telemetry.configuration import (
    TelemetryConfigurationType,
    TelemetryMetricConfiguration,
    TelemetryMetricsConfiguration,
)
from openfga_sdk.telemetry.counters import TelemetryCounter
from openfga_sdk.telemetry.histograms import TelemetryHistogram
from openfga_sdk.validation import is_well_formed_ulid_string


class ClientConfiguration(Configuration):
    """
    OpenFGA client configuration
    """

    def __init__(
        self,
        api_scheme="https",
        api_host=None,
        store_id=None,
        credentials=None,
        retry_params=None,
        authorization_model_id=None,
        ssl_ca_cert=None,
        api_url=None,  # TODO: restructure when removing api_scheme/api_host
        timeout_millisec: int | None = None,
        telemetry: (
            dict[
                TelemetryConfigurationType | str,
                TelemetryMetricsConfiguration
                | dict[
                    TelemetryHistogram | TelemetryCounter | str,
                    TelemetryMetricConfiguration
                    | dict[TelemetryAttribute | str, bool]
                    | None,
                ]
                | None,
            ]
            | None
        ) = None,
        headers: dict[str, str] | None = None,
    ):
        super().__init__(
            api_scheme,
            api_host,
            store_id,
            credentials,
            retry_params,
            ssl_ca_cert=ssl_ca_cert,
            api_url=api_url,
            timeout_millisec=timeout_millisec,
            telemetry=telemetry,
            headers=headers,
        )
        self._authorization_model_id = authorization_model_id

    def is_valid(self):
        super().is_valid()

        if (
            self.authorization_model_id is not None
            and self.authorization_model_id != ""
            and is_well_formed_ulid_string(self.authorization_model_id) is False
        ):
            raise FgaValidationException(
                f"authorization_model_id ('{self.authorization_model_id}') is not in a valid ulid format"
            )

    @property
    def authorization_model_id(self):
        return self._authorization_model_id

    @authorization_model_id.setter
    def authorization_model_id(self, value):
        self._authorization_model_id = value
