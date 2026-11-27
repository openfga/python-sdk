"""
In-memory cache of authorization models for the async client, used by BatchCheck's
`merge_equivalent_checks` option. Calls for the same model share one in-flight read.
"""

import asyncio

from collections.abc import Awaitable, Callable

from openfga_sdk.client._equivalent_checks import ModelAliases
from openfga_sdk.client._model_cache_base import (
    ModelCacheBase,
    ModelCacheKey,
    ModelLookup,
)


class AsyncModelCache(ModelCacheBase):
    """
    Model cache for the async client.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._loading: dict[ModelCacheKey, asyncio.Task] = {}

    async def get(
        self,
        key: ModelCacheKey,
        load: Callable[[], Awaitable[ModelAliases]],
    ) -> ModelLookup:
        cached = self._cached(key)
        if cached is not None:
            return cached

        task = self._loading.get(key)
        if task is None:
            task = asyncio.ensure_future(self._load(key, load))
            task.add_done_callback(_retrieve_exception)
            # An eager task can finish before it's registered, so don't keep a done one.
            if not task.done():
                self._loading[key] = task

        # Shielded, so a cancelled caller doesn't cancel the read other callers share.
        try:
            return ModelLookup(aliases=await asyncio.shield(task))
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
        load: Callable[[], Awaitable[ModelAliases]],
    ) -> ModelAliases:
        try:
            aliases = await load()
        except Exception as error:
            self._remember_failure(key, error)
            raise
        else:
            self._store(key, aliases)
            return aliases
        finally:
            if self._loading.get(key) is asyncio.current_task():
                del self._loading[key]


def _retrieve_exception(task: asyncio.Task) -> None:
    # Marks the error as seen, so asyncio doesn't log it when no caller is left waiting.
    if not task.cancelled():
        task.exception()
