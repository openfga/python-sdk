"""
The parts of the BatchCheck model cache that the async and sync clients share. Not
part of the public API.

A model never changes once it's written, so a cached model never goes stale. Only
successful reads are cached, so after a failure the next call reads again.
"""

from collections import OrderedDict
from dataclasses import dataclass

from openfga_sdk.client._equivalent_checks import ModelAliases
from openfga_sdk.exceptions import ApiException


MAX_MODELS = 32
CREDENTIAL_FAILURE_STATUSES = frozenset({401, 403})
NOT_FOUND_CODES = frozenset({"authorization_model_not_found", "store_id_not_found"})

ModelCacheKey = tuple[str, str]


class TokenRequestFailed(Exception):
    """
    The model read failed because the SDK couldn't get an access token for it. The call
    fails with `error`, as it would with the option off.
    """

    def __init__(self, error: Exception) -> None:
        super().__init__(str(error))
        self.error = error


def model_read_fails_call(error: Exception | None) -> bool:
    """
    Whether a model read error fails the BatchCheck call instead of sending the checks
    unmerged: the SDK couldn't get an access token, the model or store doesn't exist, or
    the credentials can't read the model (a 401 or 403).
    """
    if isinstance(error, TokenRequestFailed):
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
    The cached models. The async and sync caches add the reads.
    """

    def __init__(self, max_models: int = MAX_MODELS) -> None:
        self._max_models = max_models
        self._models: OrderedDict[ModelCacheKey, ModelAliases] = OrderedDict()

    def _cached(self, key: ModelCacheKey) -> ModelLookup | None:
        aliases = self._models.get(key)
        if aliases is None:
            return None
        self._models.move_to_end(key)
        return ModelLookup(aliases=aliases, hit=True)

    def _store(self, key: ModelCacheKey, aliases: ModelAliases) -> None:
        self._models[key] = aliases
        self._models.move_to_end(key)
        while len(self._models) > self._max_models:
            self._models.popitem(last=False)
