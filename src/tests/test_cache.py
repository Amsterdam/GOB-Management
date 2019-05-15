import unittest

from gobmanagement.cache import ResolveCache


class TestCache(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def test_create(self):
        cache = ResolveCache()
        self.assertEqual(cache._cache, {})

    def test_resolve(self):
        cache = ResolveCache()
        result = cache.resolve("name", 0, "query", lambda: 123)
        self.assertEqual(result, 123)
        self.assertEqual(cache._cache["name"]["response"], 123)

        cache._cache["name"]["response"] = "cached response"
        result = cache.resolve("name", 0, "query", lambda: 123)
        self.assertEqual(result, "cached response")

        result = cache.resolve("name", 1, "query", lambda: 345)
        self.assertEqual(result, 345)

        result = cache.resolve("name", 0, "query", lambda: 123)
        self.assertEqual(result, 123)
        cache._cache["name"]["response"] = "cached response"
        result = cache.resolve("name", 0, "other query", lambda: 123)
        self.assertEqual(result, 123)
