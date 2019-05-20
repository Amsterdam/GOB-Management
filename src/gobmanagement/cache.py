"""
Resolver caching

Performance critical queries can be routed through the ResolveCache

If nothing has changed the cached response will be returned
"""


class ResolveCache:

    def __init__(self):
        """
        Initialize the cache
        """
        self._cache = {}

    def resolve(self, name, id, query, get_response):
        """
        Resolve the given query out of the cache if nothing has changed
        Update the cache if the id or query has changed

        :param name: name under which the result will be cached
        :param id: identifier of the result, recompute if it has changed
        :param query: query string to execute, recompute if it has changed
        :param get_response: function to (re-)compute the response (re-exec query)
        :return: Response for the given query
        """
        response = None
        if name in self._cache:
            # Cached response exist
            cached_result = self._cache[name]
            if cached_result["id"] == id and cached_result["query"] == query:
                # No parameters have changed, respond from cache
                response = cached_result["response"]

        if response is None:
            # Recompute if no cached result exists or cache is not up to date
            self._cache[name] = {
                "id": id,
                "query": query,
                "response": get_response(),
            }

        return self._cache[name]["response"]
