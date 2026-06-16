from redis import Redis as RedisCache
from sunbot.core.cache import CacheRead


class Redis(CacheRead):
    def __init__(self, client: RedisCache):
        self._client = client

    async def get(self, key: str) -> bytes:
        data = self._client.get(key)
        if not data:
            raise KeyError
        return data.encode("utf-8") if isinstance(data, str) else data
