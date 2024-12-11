# OpenTelemetry

- [Overview](#overview)
- [Metrics](#metrics)
  - [Supported Metrics](#supported-metrics)
  - [Supported Attributes](#supported-attributes)
- [Customizing Reporting](#customizing-reporting)
- [Usage](#usage)
  - [Installation](#1-install-dependencies)
  - [Configure OpenTelemetry](#2-configure-opentelemetry)
  - [Configure OpenFGA](#3-configure-openfga)
- [Example Integration](#example-integration)

## Overview

This SDK supports [OpenTelemetry](https://opentelemetry.io/) to export [metrics](https://opentelemetry.io/docs/concepts/signals/metrics/) that provide insights into your application's performance, such as request timings. These metrics include attributes like model and store IDs, and the API called, which you can use to build detailed reports and dashboards.

If you configure the OpenTelemetry SDK, these metrics will be exported and sent to a collector as specified in your application's configuration. If OpenTelemetry is not configured, metrics functionality is disabled, and no events are sent.

## Metrics

### Supported Metrics

| Metric Name                      | Type      | Enabled by Default | Description                                                                       |
| -------------------------------- | --------- | ------------------ | --------------------------------------------------------------------------------- |
| `fga-client.request.duration`    | Histogram | Yes                | Total request time for FGA requests, in milliseconds                              |
| `fga-client.query.duration`      | Histogram | Yes                | Time taken by the FGA server to process and evaluate the request, in milliseconds |
| `fga-client.credentials.request` | Counter   | Yes                | Total number of new token requests initiated using the Client Credentials flow    |
| `fga-client.request`             | Counter   | No                 | Total number of requests made to the FGA server                                   |

### Supported Attributes

| Attribute Name                        | Type   | Enabled by Default | Description                                                                       |
| ------------------------------------- | ------ | ------------------ | --------------------------------------------------------------------------------- |
| `fga-client.request.batch_check_size` | int    | No                 | The total size of the `check` list in a `BatchCheck` call                         |
| `fga-client.request.client_id`        | string | Yes                | Client ID associated with the request, if any                                     |
| `fga-client.request.method`           | string | Yes                | FGA method/action that was performed (e.g., Check, ListObjects) in TitleCase      |
| `fga-client.request.model_id`         | string | Yes                | Authorization model ID that was sent as part of the request, if any               |
| `fga-client.request.store_id`         | string | Yes                | Store ID that was sent as part of the request                                     |
| `fga-client.response.model_id`        | string | Yes                | Authorization model ID that the FGA server used                                   |
| `fga-client.user`                     | string | No                 | User associated with the action of the request for check and list users           |
| `http.client.request.duration`        | int    | No                 | Duration for the SDK to complete the request, in milliseconds                     |
| `http.host`                           | string | Yes                | Host identifier of the origin the request was sent to                             |
| `http.request.method`                 | string | Yes                | HTTP method for the request                                                       |
| `http.request.resend_count`           | int    | Yes                | Number of retries attempted, if any                                               |
| `http.response.status_code`           | int    | Yes                | Status code of the response (e.g., `200` for success)                             |
| `http.server.request.duration`        | int    | No                 | Time taken by the FGA server to process and evaluate the request, in milliseconds |
| `url.scheme`                          | string | Yes                | HTTP scheme of the request (`http`/`https`)                                       |
| `url.full`                            | string | Yes                | Full URL of the request                                                           |
| `user_agent.original`                 | string | Yes                | User Agent used in the query                                                      |

## Customizing Reporting

To control which metrics and attributes are reported by the SDK, you can provide your own `TelemetryConfiguration` instance during initialization, as shown in the example above. The `TelemetryConfiguration` class allows you to configure the metrics and attributes that are reported by the SDK, as outlined in [the tables above](#metrics).

## Usage

### 1. Install Dependencies

Install the OpenFGA SDK and OpenTelemetry SDK in your application using `pip`:

```sh
pip install openfga opentelemetry-sdk
```

You must also install an OpenTelemetry exporter; for example, the OTLP gRPC exporter:

```sh
pip install opentelemetry-exporter-otlp-proto-grpc
```

### 2. Configure OpenTelemetry

Configure your application to use OpenTelemetry, and set up the metrics provider to export metrics using an exporter:

```python
from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider

# Configure OpenTelemetry
metrics.set_meter_provider(
    MeterProvider(
        resource=Resource(attributes={SERVICE_NAME: "openfga-example"}),
        metric_readers=[PeriodicExportingMetricReader(OTLPMetricExporter())],
    )
)
```

### 3. Configure OpenFGA

Configure the OpenFGA client, and (optionally) customize what metrics and attributes are reported:

```python
from openfga_sdk.telemetry.configuration import (
    TelemetryConfiguration,
    TelemetryMetricConfiguration,
    TelemetryMetricsConfiguration,
)
from openfga_sdk import ClientConfiguration, OpenFgaClient

configuration = ClientConfiguration(
    api_url=os.getenv("FGA_API_URL"),
    store_id=os.getenv("FGA_STORE_ID"),
    authorization_model_id=os.getenv("FGA_AUTHORIZATION_MODEL_ID"),

    # If you are comfortable with the default configuration outlined in the tables above, you can omit providing your own TelemetryConfiguration object, as one will be created for you.
    telemetry={
        "metrics": {
            "fga-client.request.duration": {
                "fga-client.request.method": True,
                "http.response.status_code": True,
            },
        },
    },
)

fga = OpenFgaClient(configuration)
```

## Example Integration

An [example integration](../example/opentelemetry) is provided that also demonstrates how to configure an application with OpenFGA and OpenTelemetry. Please refer to [the README](../example/opentelemetry/README.md) for more information.
