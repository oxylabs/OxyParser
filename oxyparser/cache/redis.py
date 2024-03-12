import json

from redis.asyncio import Redis

from oxyparser.cache.base import BaseCache
from oxyparser.settings import settings


class RedisCache(BaseCache):
    def __init__(self) -> None:
        super().__init__()
        self.redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)

    async def _get_selectors(self, domain: str) -> dict[str, list[str]]:
        return json.loads(await self.redis.get(domain)) or {}

    async def get(self, domain: str) -> dict[str, list[str]]:
        return await self._get_selectors(domain)

    async def set(self, domain: str, fields_to_selectors: dict[str, list[str]]) -> None:
        current_selectors = await self._get_selectors(domain)
        for field_name, selectors in fields_to_selectors.items():
            if field_name in current_selectors:
                current_selectors[field_name].extend(selectors)
            else:
                current_selectors[field_name] = selectors
        await self.redis.set(domain, json.dumps(current_selectors))
