import asyncio
import threading
import time

from unittest import IsolatedAsyncioTestCase, TestCase

from openfga_sdk.client.model_cache import AsyncModelCache, ModelCache


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
        self.assertEqual([(r.model, r.hit) for r in results], [("model", False)] * 3)

        later = await cache.get(KEY, load)
        self.assertEqual((later.model, later.hit, reads), ("model", True, 1))

    async def test_a_failed_read_is_remembered_for_a_short_time(self):
        clock = FakeClock()
        cache = AsyncModelCache(failure_ttl=60, clock=clock)
        reads = 0
        error = RuntimeError("forbidden")

        async def load():
            nonlocal reads
            reads += 1
            raise error

        first = await cache.get(KEY, load)
        clock.now = 59
        second = await cache.get(KEY, load)

        self.assertIs(first.error, error)
        self.assertIs(second.error, error)
        self.assertIsNone(second.model)
        self.assertEqual(reads, 1)

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

        self.assertEqual((await waiting).model, "model")
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

        self.assertEqual((await cache.get(KEY, load)).model, "model")


class TestModelCache(TestCase):
    def test_threads_share_one_read_and_later_lookups_hit(self):
        cache = ModelCache()
        started = threading.Event()
        release = threading.Event()
        reads = 0

        def load():
            nonlocal reads
            reads += 1
            started.set()
            release.wait()
            return "model"

        results = []
        owner = threading.Thread(target=lambda: results.append(cache.get(KEY, load)))
        owner.start()
        started.wait()
        waiters = [
            threading.Thread(target=lambda: results.append(cache.get(KEY, load)))
            for _ in range(3)
        ]
        for waiter in waiters:
            waiter.start()
        release.set()
        for thread in [owner, *waiters]:
            thread.join()

        self.assertEqual(reads, 1)
        self.assertEqual([r.model for r in results], ["model"] * 4)
        self.assertTrue(cache.get(KEY, load).hit)

    def test_a_failed_read_is_remembered_for_a_short_time(self):
        clock = FakeClock()
        cache = ModelCache(failure_ttl=60, clock=clock)
        reads = 0
        error = RuntimeError("forbidden")

        def load():
            nonlocal reads
            reads += 1
            raise error

        self.assertIs(cache.get(KEY, load).error, error)
        clock.now = 59
        self.assertIs(cache.get(KEY, load).error, error)
        self.assertEqual(reads, 1)

        clock.now = 60
        cache.get(KEY, load)
        self.assertEqual(reads, 2)

    def test_drops_the_least_recently_used_model(self):
        cache = ModelCache(max_models=2)

        def get(key):
            return cache.get(key, lambda: f"model-{key}")

        get("a")
        get("b")
        self.assertTrue(get("a").hit)
        get("c")

        self.assertTrue(get("a").hit)
        self.assertFalse(get("b").hit)

    def test_threads_waiting_on_a_failed_read_get_its_error(self):
        cache = ModelCache()
        started = threading.Event()
        release = threading.Event()
        error = RuntimeError("forbidden")

        def load():
            started.set()
            release.wait()
            raise error

        results = []
        owner = threading.Thread(target=lambda: results.append(cache.get(KEY, load)))
        owner.start()
        started.wait()
        waiters = [
            threading.Thread(target=lambda: results.append(cache.get(KEY, load)))
            for _ in range(3)
        ]
        for waiter in waiters:
            waiter.start()
        time.sleep(0.05)
        release.set()
        for thread in [owner, *waiters]:
            thread.join()

        self.assertEqual([r.error for r in results], [error] * 4)

    def test_remembers_a_bounded_number_of_failures(self):
        cache = ModelCache(max_models=2)
        reads = []

        def get(key):
            def load():
                reads.append(key)
                raise RuntimeError(key)

            return cache.get(key, load)

        get("a")
        get("b")
        get("c")
        get("b")
        get("c")
        self.assertEqual(reads, ["a", "b", "c"])

        get("a")
        self.assertEqual(reads, ["a", "b", "c", "a"])

    def test_an_interrupted_read_is_not_cached(self):
        cache = ModelCache()

        def interrupt():
            raise KeyboardInterrupt()

        with self.assertRaises(KeyboardInterrupt):
            cache.get(KEY, interrupt)

        self.assertEqual(cache.get(KEY, lambda: "model").model, "model")
