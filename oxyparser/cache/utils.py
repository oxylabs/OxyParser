from typing import Literal

from oxyparser.cache.file import FileCache
from oxyparser.cache.redis import RedisCache


def get_cache(cache_type: Literal["file", "redis"] | None) -> FileCache | RedisCache | None:
    mapping = {"file": FileCache, "redis": RedisCache}

    cache_cls = mapping.get(str(cache_type))
    if not cache_cls:
        return FileCache()
    return cache_cls()
