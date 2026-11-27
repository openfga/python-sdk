import asyncio
import sys

from types import SimpleNamespace
from unittest import IsolatedAsyncioTestCase, TestCase, skipIf

from openfga_sdk.client._model_cache import AsyncModelCache
from openfga_sdk.client._model_cache_base import model_read_fails_call
from openfga_sdk.exceptions import (
    ForbiddenException,
    NotFoundException,
    RateLimitExceededError,
    ServiceException,
    UnauthorizedException,
    ValidationException,
)


KEY = ("store", "model")


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


class TestAsyncModelCache(IsolatedAsyncioTestCase):
    async def test_parallel_lookups_share_one_read_and_later_lookups_hit(self):
        cache = AsyncModelCache()
        release = asyncio.Event()
        reads = 0

        async def load():
            nonlocal reads
            reads += 1
            await release.wait()
            return "model"

        lookups = [asyncio.ensure_future(cache.get(KEY, load)) for _ in range(3)]
        await asyncio.sleep(0)
        release.set()
        results = await asyncio.gather(*lookups)

        self.assertEqual(reads, 1)
        self.assertEqual([(r.aliases, r.hit) for r in results], [("model", False)] * 3)

        later = await cache.get(KEY, load)
        self.assertEqual((later.aliases, later.hit, reads), ("model", True, 1))

    async def test_a_failed_read_is_remembered_for_a_short_time(self):
        clock = FakeClock()
        cache = AsyncModelCache(failure_ttl=60, clock=clock)
        reads = 0
        error = RateLimitExceededError(status=429)

        async def load():
            nonlocal reads
            reads += 1
            raise error

        first = await cache.get(KEY, load)
        clock.now = 59
        second = await cache.get(KEY, load)

        self.assertIs(first.error, error)
        self.assertIs(second.error, error)
        self.assertIsNone(second.aliases)
        self.assertEqual(reads, 1)

        clock.now = 60
        await cache.get(KEY, load)
        self.assertEqual(reads, 2)

    @skipIf(sys.version_info < (3, 12), "eager tasks need Python 3.12+")
    async def test_retries_a_failed_read_that_finished_eagerly(self):
        asyncio.get_running_loop().set_task_factory(asyncio.eager_task_factory)
        clock = FakeClock()
        cache = AsyncModelCache(failure_ttl=60, clock=clock)
        reads = 0

        async def load():
            nonlocal reads
            reads += 1
            raise RuntimeError("forbidden")

        await cache.get(KEY, load)
        self.assertEqual(cache._loading, {})

        clock.now = 60
        await cache.get(KEY, load)
        self.assertEqual(reads, 2)

    async def test_drops_the_least_recently_used_model(self):
        cache = AsyncModelCache(max_models=2)

        async def load_for(key):
            async def load():
                return f"model-{key}"

            return await cache.get(key, load)

        await load_for("a")
        await load_for("b")
        self.assertTrue((await load_for("a")).hit)
        await load_for("c")

        self.assertTrue((await load_for("a")).hit)
        self.assertFalse((await load_for("b")).hit)

    async def test_a_cancelled_caller_does_not_cancel_the_shared_read(self):
        cache = AsyncModelCache()
        release = asyncio.Event()

        async def load():
            await release.wait()
            return "model"

        cancelled = asyncio.ensure_future(cache.get(KEY, load))
        waiting = asyncio.ensure_future(cache.get(KEY, load))
        await asyncio.sleep(0)
        cancelled.cancel()
        release.set()

        self.assertEqual((await waiting).aliases, "model")
        with self.assertRaises(asyncio.CancelledError):
            await cancelled

    async def test_close_cancels_in_flight_reads_without_caching_them(self):
        cache = AsyncModelCache()
        started = asyncio.Event()

        async def hang():
            started.set()
            await asyncio.Event().wait()

        lookup = asyncio.ensure_future(cache.get(KEY, hang))
        await started.wait()
        await cache.close()

        with self.assertRaises(asyncio.CancelledError):
            await lookup

        async def load():
            return "model"

        self.assertEqual((await cache.get(KEY, load)).aliases, "model")

    async def test_keys_on_both_the_store_and_the_model(self):
        clock = FakeClock()
        cache = AsyncModelCache(clock=clock)
        reads = []

        async def get(store, model, error=None):
            async def load():
                reads.append((store, model))
                if error is not None:
                    raise error
                return f"{store}/{model}"

            return await cache.get((store, model), load)

        self.assertEqual((await get("a", "1")).aliases, "a/1")
        self.assertEqual((await get("b", "1")).aliases, "b/1")
        self.assertEqual((await get("a", "2")).aliases, "a/2")
        self.assertTrue((await get("a", "1")).hit)
        self.assertTrue((await get("b", "1")).hit)
        self.assertTrue((await get("a", "2")).hit)
        self.assertEqual(reads, [("a", "1"), ("b", "1"), ("a", "2")])

        await get("c", "1", RateLimitExceededError(status=429))
        self.assertEqual((await get("d", "1")).aliases, "d/1")
        self.assertEqual((await get("c", "2")).aliases, "c/2")
        self.assertEqual(reads[3:], [("c", "1"), ("d", "1"), ("c", "2")])


def with_code(error, code):
    error.parsed_exception = SimpleNamespace(code=code)
    return error


class TestModelReadFailsCall(TestCase):
    def test_fails_when_the_model_is_missing_or_the_credentials_cannot_read_it(self):
        for error, fails in [
            (
                with_code(
                    ValidationException(status=400), "authorization_model_not_found"
                ),
                True,
            ),
            (with_code(NotFoundException(status=404), "store_id_not_found"), True),
            (UnauthorizedException(status=401), True),
            (ForbiddenException(status=403), True),
            (with_code(ValidationException(status=400), "validation_error"), False),
            (RateLimitExceededError(status=429), False),
            (ServiceException(status=500), False),
            (TimeoutError(), False),
            (ValueError("The authorization model response is empty"), False),
            (None, False),
        ]:
            with self.subTest(error=repr(error)):
                self.assertEqual(model_read_fails_call(error), fails)
