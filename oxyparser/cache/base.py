from collections import defaultdict
from typing import Any


class BaseCache:
    def __init__(self) -> None:
        self._cache: dict[str, Any] = defaultdict(list)

    async def get(self, domain: str) -> dict[str, list[str]]:
        return self._cache.get(domain) or {}

    async def set(self, domain: str, fields_to_selectors: dict[str, list[str]]) -> None:
        self._cache[domain].append(fields_to_selectors)
