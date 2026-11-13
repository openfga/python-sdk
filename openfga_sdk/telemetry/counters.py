from typing import NamedTuple


class TelemetryCounter(NamedTuple):
    name: str
    description: str
    unit: str = ""


class TelemetryCounters:
    fga_client_credentials_request: TelemetryCounter = TelemetryCounter(
        name="fga-client.credentials.request",
        description="Total number of new token requests initiated using the Client Credentials flow.",
    )

    fga_client_request: TelemetryCounter = TelemetryCounter(
        name="fga-client.request",
        description="Total number of requests made to the FGA server.",
    )

    fga_client_batch_check_checks_requested: TelemetryCounter = TelemetryCounter(
        name="fga-client.batch_check.checks_requested",
        description="Total number of checks passed to BatchCheck with merge_equivalent_checks on.",
    )

    fga_client_batch_check_checks_sent: TelemetryCounter = TelemetryCounter(
        name="fga-client.batch_check.checks_sent",
        description="Total number of checks sent by BatchCheck with merge_equivalent_checks on.",
    )

    fga_client_model_cache_lookup: TelemetryCounter = TelemetryCounter(
        name="fga-client.model_cache.lookup",
        description="Total number of authorization model cache lookups.",
    )

    fga_client_batch_check_merge_fallback: TelemetryCounter = TelemetryCounter(
        name="fga-client.batch_check.merge_fallback",
        description="Total number of BatchCheck calls sent unmerged because the authorization model couldn't be read.",
    )

    _counters: list[TelemetryCounter] = [
        fga_client_credentials_request,
        fga_client_request,
        fga_client_batch_check_checks_requested,
        fga_client_batch_check_checks_sent,
        fga_client_model_cache_lookup,
        fga_client_batch_check_merge_fallback,
    ]

    @staticmethod
    def getAll() -> list[TelemetryCounter]:
        return TelemetryCounters._counters

    @staticmethod
    def get(
        name: str | None = None,
    ) -> TelemetryCounter | None:
        for counter in TelemetryCounters._counters:
            if counter.name == name:
                return counter

        return None
