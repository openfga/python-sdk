import threading
import time

from unittest import TestCase

from openfga_sdk.exceptions import (
    ForbiddenException,
    RateLimitExceededError,
    ServiceException,
    UnauthorizedException,
    ValidationException,
)
from openfga_sdk.sync.client._model_cache import ModelCache


KEY = ("store", "model")


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
        self.assertEqual([r.aliases for r in results], ["model"] * 4)
        self.assertTrue(cache.get(KEY, load).hit)

    def test_a_failed_read_is_not_cached(self):
        for error in [
            RateLimitExceededError(status=429),
            ForbiddenException(status=403),
            UnauthorizedException(status=401),
            ValidationException(status=400),
            ServiceException(status=500),
            TimeoutError(),
        ]:
            with self.subTest(error=type(error).__name__):
                cache = ModelCache()
                reads = 0

                def load():
                    nonlocal reads
                    reads += 1
                    raise error

                self.assertIs(cache.get(KEY, load).error, error)
                self.assertIs(cache.get(KEY, load).error, error)
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

    def test_an_interrupted_read_is_not_cached(self):
        cache = ModelCache()

        def interrupt():
            raise KeyboardInterrupt()

        with self.assertRaises(KeyboardInterrupt):
            cache.get(KEY, interrupt)

        self.assertEqual(cache.get(KEY, lambda: "model").aliases, "model")

    def test_keys_on_both_the_store_and_the_model(self):
        cache = ModelCache()
        reads = []

        def get(store, model, error=None):
            def load():
                reads.append((store, model))
                if error is not None:
                    raise error
                return f"{store}/{model}"

            return cache.get((store, model), load)

        self.assertEqual(get("a", "1").aliases, "a/1")
        self.assertEqual(get("b", "1").aliases, "b/1")
        self.assertEqual(get("a", "2").aliases, "a/2")
        self.assertTrue(get("a", "1").hit)
        self.assertTrue(get("b", "1").hit)
        self.assertTrue(get("a", "2").hit)
        self.assertEqual(reads, [("a", "1"), ("b", "1"), ("a", "2")])

        get("c", "1", RateLimitExceededError(status=429))
        self.assertEqual(get("d", "1").aliases, "d/1")
        self.assertEqual(get("c", "2").aliases, "c/2")
        self.assertEqual(reads[3:], [("c", "1"), ("d", "1"), ("c", "2")])
