from sunbot.core.cache import CacheRead
from sunbot.std.concurrency import run_sync


class InMemoryCache(CacheRead):
    def __init__(self):
        self._cache: dict[str, bytes] = {}

    async def get(self, key: str) -> bytes:
        _data = await run_sync(self._get, key)
        if not _data:
            raise KeyError
        return _data

    def _get(self, key: str) -> bytes | None:
        return self._cache.get(key)
