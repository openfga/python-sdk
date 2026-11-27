"""
Steps of a BatchCheck call with `merge_equivalent_checks` on that are the same in the
async and sync clients. The clients only read the model and send the checks. Not part
of the public API.
"""

import logging

from openfga_sdk.client._equivalent_checks import (
    EquivalentCheckGroup,
    resolve,
    unmerged,
)
from openfga_sdk.client._model_cache_base import ModelLookup, model_read_fails_call
from openfga_sdk.client.models.batch_check_item import ClientBatchCheckItem
from openfga_sdk.telemetry.attributes import TelemetryAttributes


logger = logging.getLogger(__name__)


def log_model_read_failure(
    error: Exception, store_id: str, authorization_model_id: str
) -> None:
    """
    Warn that the checks go out unmerged, unless the error fails the call.
    """
    if model_read_fails_call(error):
        return
    logger.warning(
        "merge_equivalent_checks: couldn't read authorization model %s in store %s (status: %s). "
        "Sending checks unmerged.",
        authorization_model_id,
        store_id,
        getattr(error, "status", None),
    )


def checks_to_send(
    api_client,
    store_id: str,
    authorization_model_id: str,
    lookup: ModelLookup,
    checks: list[ClientBatchCheckItem],
) -> list[EquivalentCheckGroup]:
    """
    Group the checks using the model from the cache, or send them unmerged if the model
    couldn't be read or grouping failed. Raise if the model read error fails the call.
    """
    metrics = _MergeMetrics(api_client, store_id, authorization_model_id)
    metrics.model_cache_lookup(lookup.hit)

    if lookup.aliases is None:
        if model_read_fails_call(lookup.error):
            # BatchCheck would fail too if the model is missing or no token can be
            # fetched, and falling back on a 401 or 403 would hide wrong credentials.
            # Fail before sending anything.
            raise lookup.error
        groups = unmerged(checks)
        metrics.fallback(getattr(lookup.error, "status", None))
    else:
        try:
            groups = resolve(lookup.aliases, checks)
        except Exception:
            logger.warning(
                "merge_equivalent_checks: couldn't group the checks. Sending checks unmerged.",
                exc_info=True,
            )
            groups = unmerged(checks)
            metrics.fallback(None)

    # Every chunk is sent even if another one fails, so count them up front.
    metrics.checks(requested=len(checks), sent=len(groups))
    return groups


class _MergeMetrics:
    def __init__(self, api_client, store_id: str, authorization_model_id: str) -> None:
        self._metrics = api_client._telemetry.metrics
        self._configuration = api_client.configuration.telemetry
        self._attributes = {
            TelemetryAttributes.fga_client_request_store_id: store_id,
            TelemetryAttributes.fga_client_request_model_id: authorization_model_id,
        }

    def model_cache_lookup(self, hit: bool) -> None:
        self._metrics.modelCacheLookup(
            attributes={
                **self._attributes,
                TelemetryAttributes.fga_client_model_cache_result: (
                    "hit" if hit else "miss"
                ),
            },
            configuration=self._configuration,
        )

    def fallback(self, status: int | None) -> None:
        self._metrics.batchCheckMergeFallback(
            attributes={
                **self._attributes,
                TelemetryAttributes.http_response_status_code: status,
            },
            configuration=self._configuration,
        )

    def checks(self, requested: int, sent: int) -> None:
        self._metrics.batchCheckChecksRequested(
            requested, attributes=self._attributes, configuration=self._configuration
        )
        self._metrics.batchCheckChecksSent(
            sent, attributes=self._attributes, configuration=self._configuration
        )
