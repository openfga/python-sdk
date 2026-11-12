"""
In-memory cache of authorization models, used by BatchCheck's `merge_equivalent_checks` option.

A model never changes once it's written, so a cached model never goes stale. Only
successful reads are cached. A failed read is remembered for a short time, so missing
read access doesn't add a read to every call. Calls for the same model share one
in-flight read.
"""

import asyncio
import threading
import time

from collections import OrderedDict
from collections.abc import Awaitable, Callable
from concurrent.futures import Future
from dataclasses import dataclass

from openfga_sdk.models.authorization_model import AuthorizationModel


MAX_MODELS = 32
FAILURE_TTL_SECONDS = 60.0

ModelCacheKey = tuple[str, str]


@dataclass
class ModelLookup:
    """
    The result of a cache lookup: the model, or the error from reading it.
    `hit` is True only when the model was already in the cache.
    """

    model: AuthorizationModel | None = None
    hit: bool = False
    error: Exception | None = None


class _ModelCacheState:
    def __init__(
        self,
        max_models: int = MAX_MODELS,
        failure_ttl: float = FAILURE_TTL_SECONDS,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._max_models = max_models
        self._failure_ttl = failure_ttl
        self._clock = clock
        self._models: OrderedDict[ModelCacheKey, AuthorizationModel] = OrderedDict()
        self._failures: OrderedDict[ModelCacheKey, tuple[float, Exception]] = (
            OrderedDict()
        )

    def _cached(self, key: ModelCacheKey) -> ModelLookup | None:
        model = self._models.get(key)
        if model is not None:
            self._models.move_to_end(key)
            return ModelLookup(model=model, hit=True)

        failure = self._failures.get(key)
        if failure is not None:
            expires_at, error = failure
            if self._clock() < expires_at:
                return ModelLookup(error=error)
            del self._failures[key]

        return None

    def _store(self, key: ModelCacheKey, model: AuthorizationModel) -> None:
        self._failures.pop(key, None)
        self._models[key] = model
        self._models.move_to_end(key)
        while len(self._models) > self._max_models:
            self._models.popitem(last=False)

    def _remember_failure(self, key: ModelCacheKey, error: Exception) -> None:
        self._failures[key] = (self._clock() + self._failure_ttl, error)
        self._failures.move_to_end(key)
        while len(self._failures) > self._max_models:
            self._failures.popitem(last=False)


class AsyncModelCache(_ModelCacheState):
    """
    Model cache for the async client.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._loading: dict[ModelCacheKey, asyncio.Task] = {}

    async def get(
        self,
        key: ModelCacheKey,
        load: Callable[[], Awaitable[AuthorizationModel]],
    ) -> ModelLookup:
        cached = self._cached(key)
        if cached is not None:
            return cached

        task = self._loading.get(key)
        if task is None:
            task = asyncio.ensure_future(self._load(key, load))
            task.add_done_callback(_retrieve_exception)
            self._loading[key] = task

        # Shielded, so a cancelled caller doesn't cancel the read other callers share.
        try:
            return ModelLookup(model=await asyncio.shield(task))
        except asyncio.CancelledError:
            raise
        except Exception as error:
            return ModelLookup(error=error)

    async def close(self) -> None:
        """
        Cancel in-flight reads.
        """
        tasks = list(self._loading.values())
        self._loading.clear()
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _load(
        self,
        key: ModelCacheKey,
        load: Callable[[], Awaitable[AuthorizationModel]],
    ) -> AuthorizationModel:
        try:
            model = await load()
        except Exception as error:
            self._remember_failure(key, error)
            raise
        else:
            self._store(key, model)
            return model
        finally:
            if self._loading.get(key) is asyncio.current_task():
                del self._loading[key]


class ModelCache(_ModelCacheState):
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
        load: Callable[[], AuthorizationModel],
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
                return ModelLookup(model=future.result())
            except Exception as error:
                return ModelLookup(error=error)

        try:
            model = load()
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
            self._store(key, model)
            self._loading.pop(key, None)
        future.set_result(model)
        return ModelLookup(model=model)


def _retrieve_exception(task: asyncio.Task) -> None:
    # Marks the error as seen, so asyncio doesn't log it when no caller is left waiting.
    if not task.cancelled():
        task.exception()
