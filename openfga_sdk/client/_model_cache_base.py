"""
The parts of the BatchCheck model cache that the async and sync clients share. Not
part of the public API.

A model never changes once it's written, so a cached model never goes stale. Only
successful reads are cached. A 429 is remembered for a short time, so rate limiting
doesn't add a read to every call. Other failures aren't, so the next call reads again.
"""

import time

from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass

from openfga_sdk.client.equivalent_checks import ModelAliases
from openfga_sdk.exceptions import ApiException, AuthenticationError


MAX_MODELS = 32
FAILURE_TTL_SECONDS = 60.0
REMEMBERED_FAILURE_STATUSES = frozenset({429})
CREDENTIAL_FAILURE_STATUSES = frozenset({401, 403})
NOT_FOUND_CODES = frozenset({"authorization_model_not_found", "store_id_not_found"})

ModelCacheKey = tuple[str, str]


def model_read_fails_call(error: Exception | None) -> bool:
    """
    Whether a model read error fails the BatchCheck call instead of sending the checks
    unmerged: the model or store doesn't exist, or the credentials can't read the model
    (a 401 or 403, or the token request failed)
    """
    if isinstance(error, AuthenticationError):
        return True
    return isinstance(error, ApiException) and (
        error.code in NOT_FOUND_CODES or error.status in CREDENTIAL_FAILURE_STATUSES
    )


@dataclass
class ModelLookup:
    """
    The result of a cache lookup: the model's aliases, or the error from reading it.
    `hit` is True only when they were already in the cache.
    """

    aliases: ModelAliases | None = None
    hit: bool = False
    error: Exception | None = None


class ModelCacheBase:
    """
    The cached models and remembered failures. The async and sync caches add the reads.
    """

    def __init__(
        self,
        max_models: int = MAX_MODELS,
        failure_ttl: float = FAILURE_TTL_SECONDS,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._max_models = max_models
        self._failure_ttl = failure_ttl
        self._clock = clock
        self._models: OrderedDict[ModelCacheKey, ModelAliases] = OrderedDict()
        self._failures: OrderedDict[ModelCacheKey, tuple[float, Exception]] = (
            OrderedDict()
        )

    def _cached(self, key: ModelCacheKey) -> ModelLookup | None:
        aliases = self._models.get(key)
        if aliases is not None:
            self._models.move_to_end(key)
            return ModelLookup(aliases=aliases, hit=True)

        failure = self._failures.get(key)
        if failure is not None:
            expires_at, error = failure
            if self._clock() < expires_at:
                return ModelLookup(error=error)
            del self._failures[key]

        return None

    def _store(self, key: ModelCacheKey, aliases: ModelAliases) -> None:
        self._failures.pop(key, None)
        self._models[key] = aliases
        self._models.move_to_end(key)
        while len(self._models) > self._max_models:
            self._models.popitem(last=False)

    def _remember_failure(self, key: ModelCacheKey, error: Exception) -> None:
        if not (
            isinstance(error, ApiException)
            and error.status in REMEMBERED_FAILURE_STATUSES
        ):
            return
        self._failures[key] = (self._clock() + self._failure_ttl, error)
        self._failures.move_to_end(key)
        while len(self._failures) > self._max_models:
            self._failures.popitem(last=False)
