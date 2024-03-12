import pytest
from aiofiles import os

from oxyparser.cache.file import FileCache


@pytest.mark.asyncio
async def test_it_saves_cached_selectors_for_domain() -> None:
    cache = FileCache()
    domain = "example.com"
    fields_to_selectors = {
        "name": ["#name"],
        "surname": ["#surname"],
        "address": ["#address"],
        "age": ["#age"],
        "pets": ["#pets"],
    }
    await cache.set(domain, fields_to_selectors)

    cached_fields_to_selectors = await cache.get(domain)

    for field, selectors in fields_to_selectors.items():
        selector = selectors[0]
        assert selector in cached_fields_to_selectors[field]

    await os.remove(f"_oxyparser_cache_{domain}")
