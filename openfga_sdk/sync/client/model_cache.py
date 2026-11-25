"""
In-memory cache of authorization models for the sync client, used by BatchCheck's
`merge_equivalent_checks` option. Calls for the same model share one in-flight read.
"""

import threading

from collections.abc import Callable
from concurrent.futures import Future

from openfga_sdk.client._model_cache_base import (
    ModelCacheBase,
    ModelCacheKey,
    ModelLookup,
)
from openfga_sdk.client.equivalent_checks import ModelAliases


class ModelCache(ModelCacheBase):
    """
    Model cache for the sync client. Safe to share across threads.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._lock = threading.Lock()
        self._loading: dict[ModelCacheKey, Future] = {}

    def get(
        self,
        key: ModelCacheKey,
        load: Callable[[], ModelAliases],
    ) -> ModelLookup:
        with self._lock:
            cached = self._cached(key)
            if cached is not None:
                return cached

            future = self._loading.get(key)
            owner = future is None
            if owner:
                future = Future()
                self._loading[key] = future

        if not owner:
            try:
                return ModelLookup(aliases=future.result())
            except Exception as error:
                return ModelLookup(error=error)

        try:
            aliases = load()
        except Exception as error:
            with self._lock:
                self._remember_failure(key, error)
                self._loading.pop(key, None)
            future.set_exception(error)
            return ModelLookup(error=error)
        except BaseException:
            with self._lock:
                self._loading.pop(key, None)
            future.set_exception(
                RuntimeError("Reading the authorization model was interrupted")
            )
            raise

        with self._lock:
            self._store(key, aliases)
            self._loading.pop(key, None)
        future.set_result(aliases)
        return ModelLookup(aliases=aliases)
