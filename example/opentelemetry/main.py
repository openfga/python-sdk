import asyncio
import os
import sys
from operator import attrgetter
from random import randint
from typing import Any

from dotenv import load_dotenv
from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

from openfga_sdk.telemetry.configuration import (
    TelemetryConfiguration,
    TelemetryMetricConfiguration,
    TelemetryMetricsConfiguration,
)

# For usage convenience of this example, we will import the OpenFGA SDK from the parent directory.
sdk_path = os.path.realpath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
sys.path.insert(0, sdk_path)

from openfga_sdk import (
    ClientConfiguration,
    OpenFgaClient,
    ReadRequestTupleKey,
)
from openfga_sdk.client.models import ClientCheckRequest
from openfga_sdk.credentials import (
    CredentialConfiguration,
    Credentials,
)
from openfga_sdk.exceptions import FgaValidationException


class app:
    """
    An example class to demonstrate how to implement the OpenFGA SDK with OpenTelemetry.
    """

    def __init__(
        self,
        client: OpenFgaClient = None,
        credentials: Credentials = None,
        configuration: ClientConfiguration = None,
        telemetry: TelemetryConfiguration = None,
    ):
        """
        Initialize the example with the provided client, credentials, and configuration.
        """

        self._client = client
        self._credentials = credentials
        self._configuration = configuration
        self._telemetry = telemetry

    async def fga_client(self, env: dict[str, str] = {}) -> OpenFgaClient:
        """
        Build an OpenFGA client with the provided credentials and configuration. If not provided, load from environment variables.
        """

        if not self._client or not self._credentials or not self._configuration:
            load_dotenv()

            if not self._credentials:
                self._credentials = Credentials(
                    method="client_credentials",
                    configuration=CredentialConfiguration(
                        client_id=os.getenv("FGA_CLIENT_ID"),
                        client_secret=os.getenv("FGA_CLIENT_SECRET"),
                        api_issuer=os.getenv("FGA_API_TOKEN_ISSUER"),
                        api_audience=os.getenv("FGA_API_AUDIENCE"),
                    ),
                )

            if not self._configuration:
                self._configuration = ClientConfiguration(
                    api_url=os.getenv("FGA_API_URL"),
                    store_id=os.getenv("FGA_STORE_ID"),
                    authorization_model_id=os.getenv("FGA_AUTHORIZATION_MODEL_ID"),
                    credentials=self._credentials,
                )

            if not self._telemetry:
                # Configure the telemetry metrics to be collected.
                # Note: the following represents the default configuration values, so unless you want to change them, you can omit this step.
                self._telemetry = TelemetryConfiguration(
                    metrics=TelemetryMetricsConfiguration(
                        counter_credentials_request=TelemetryMetricConfiguration(
                            attr_fga_client_request_client_id=True,
                            attr_fga_client_request_method=True,
                            attr_fga_client_request_model_id=True,
                            attr_fga_client_request_store_id=True,
                            attr_fga_client_response_model_id=True,
                            attr_fga_client_user=False,
                            attr_http_client_request_duration=False,
                            attr_http_host=True,
                            attr_http_request_method=True,
                            attr_http_request_resend_count=True,
                            attr_http_response_status_code=True,
                            attr_http_server_request_duration=False,
                            attr_http_url_scheme=True,
                            attr_http_url_full=True,
                            attr_user_agent_original=True,
                        ),
                        histogram_request_duration=TelemetryMetricConfiguration(
                            attr_fga_client_request_client_id=True,
                            attr_fga_client_request_method=True,
                            attr_fga_client_request_model_id=True,
                            attr_fga_client_request_store_id=True,
                            attr_fga_client_response_model_id=True,
                            attr_fga_client_user=False,
                            attr_http_client_request_duration=False,
                            attr_http_host=True,
                            attr_http_request_method=True,
                            attr_http_request_resend_count=True,
                            attr_http_response_status_code=True,
                            attr_http_server_request_duration=False,
                            attr_http_url_scheme=True,
                            attr_http_url_full=True,
                            attr_user_agent_original=True,
                        ),
                        histogram_query_duration=TelemetryMetricConfiguration(
                            attr_fga_client_request_client_id=True,
                            attr_fga_client_request_method=True,
                            attr_fga_client_request_model_id=True,
                            attr_fga_client_request_store_id=True,
                            attr_fga_client_response_model_id=True,
                            attr_fga_client_user=False,
                            attr_http_client_request_duration=False,
                            attr_http_host=True,
                            attr_http_request_method=True,
                            attr_http_request_resend_count=True,
                            attr_http_response_status_code=True,
                            attr_http_server_request_duration=False,
                            attr_http_url_scheme=True,
                            attr_http_url_full=True,
                            attr_user_agent_original=True,
                        ),
                    ),
                )

                self._configuration.telemetry = self._telemetry

            if not self._client:
                return OpenFgaClient(self._configuration)

        return self._client

    def configure_telemetry(self) -> None:
        """
        Configure OpenTelemetry with the provided meter provider.
        """

        exporters = []
        exporters.append(PeriodicExportingMetricReader(OTLPMetricExporter()))

        if os.getenv("OTEL_EXPORTER_CONSOLE") == "true":
            exporters.append(PeriodicExportingMetricReader(ConsoleMetricExporter()))

        metrics.set_meter_provider(
            MeterProvider(
                resource=Resource(attributes={SERVICE_NAME: "openfga-python-example"}),
                metric_readers=[exporter for exporter in exporters],
            )
        )

    def unpack(
        self,
        response,
        attr: str,
    ) -> Any:
        """
        Shortcut to unpack a FGA response and return the desired attribute.
        Note: This is a simple example and does not handle errors or exceptions.
        """

        return attrgetter(attr)(response)


async def main():
    app().configure_telemetry()

    async with await app().fga_client() as fga_client:
        print("Client created successfully.")

        print("Reading authorization model ...", end=" ")
        authorization_models = app().unpack(
            await fga_client.read_authorization_models(), "authorization_models"
        )
        print(f"Done! Models Count: {len(authorization_models)}")

        print("Reading tuples ...", end=" ")
        tuples = app().unpack(await fga_client.read(ReadRequestTupleKey()), "tuples")
        print(f"Done! Tuples Count: {len(tuples)}")

        checks_requests = randint(1, 10)

        print(f"Making {checks_requests} checks ...", end=" ")
        for _ in range(checks_requests):
            try:
                allowed = app().unpack(
                    await fga_client.check(
                        body=ClientCheckRequest(
                            user="user:anne", relation="owner", object="folder:foo"
                        ),
                    ),
                    "allowed",
                )
            except FgaValidationException as error:
                print(f"Checked failed due to validation exception: {error}")
        print("Done!")


asyncio.run(main())
