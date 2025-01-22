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
from openfga_sdk.telemetry.configuration import TelemetryConfiguration


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
                    authorization_model_id=os.getenv("FGA_AUTHORIZATION_MODEL_ID"),
                    credentials=self._credentials,
                )

            if not self._telemetry:
                # Configure the telemetry metrics to be collected.
                # Note: the following represents the default configuration values, so unless you want to customize what's reported, you can omit this.
                self._telemetry = {
                    "metrics": {
                        "fga-client.credentials.request": {
                            "fga-client.request.client_id": True,
                            "fga-client.request.method": True,
                            "fga-client.request.model_id": True,
                            "fga-client.request.store_id": True,
                            "fga-client.response.model_id": True,
                            "fga-client.user": False,
                            "http.client.request.duration": False,
                            "http.host": True,
                            "http.request.method": True,
                            "http.request.resend_count": True,
                            "http.response.status_code": True,
                            "http.server.request.duration": False,
                            "url.scheme": True,
                            "url.full": True,
                            "user_agent.original": True,
                        },
                        "fga-client.request.duration": {
                            "fga-client.request.client_id": True,
                            "fga-client.request.method": True,
                            "fga-client.request.model_id": True,
                            "fga-client.request.store_id": True,
                            "fga-client.response.model_id": True,
                            "fga-client.user": False,
                            "http.client.request.duration": False,
                            "http.host": True,
                            "http.request.method": True,
                            "http.request.resend_count": True,
                            "http.response.status_code": True,
                            "http.server.request.duration": False,
                            "url.scheme": True,
                            "url.full": True,
                            "user_agent.original": True,
                        },
                        "fga-client.query.duration": {
                            "fga-client.request.client_id": True,
                            "fga-client.request.method": True,
                            "fga-client.request.model_id": True,
                            "fga-client.request.store_id": True,
                            "fga-client.response.model_id": True,
                            "fga-client.user": False,
                            "http.client.request.duration": False,
                            "http.host": True,
                            "http.request.method": True,
                            "http.request.resend_count": True,
                            "http.response.status_code": True,
                            "http.server.request.duration": False,
                            "url.scheme": True,
                            "url.full": True,
                            "user_agent.original": True,
                        },
                    }
                }

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
            await fga_client.read_authorization_models(
                {
                    "store_id": os.getenv("FGA_STORE_ID"),
                }
            ),
            "authorization_models",
        )
        print(f"Done! Models Count: {len(authorization_models)}")

        print("Reading tuples ...", end=" ")
        tuples = app().unpack(
            await fga_client.read(
                ReadRequestTupleKey(),
                {
                    "store_id": os.getenv("FGA_STORE_ID"),
                },
            ),
            "tuples",
        )
        print(f"Done! Tuples Count: {len(tuples)}")

        checks_requests = randint(1, 10)

        print(f"Making {checks_requests} checks ...", end=" ")
        for _ in range(checks_requests):
            try:
                allowed = app().unpack(
                    await fga_client.check(
                        ClientCheckRequest(
                            user="user:anne", relation="owner", object="folder:foo"
                        ),
                        {
                            "store_id": os.getenv("FGA_STORE_ID"),
                        },
                    ),
                    "allowed",
                )
            except FgaValidationException as error:
                print(f"Checked failed due to validation exception: {error}")
        print("Done!")


asyncio.run(main())
