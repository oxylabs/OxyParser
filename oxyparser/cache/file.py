import json

import aiofiles

from oxyparser.cache.base import BaseCache


class FileCache(BaseCache):
    async def _read_from_file(self, domain: str) -> dict[str, list[str]]:
        async with aiofiles.open(f"_oxyparser_cache_{domain}", "r") as file:
            contents = await file.read()
            return json.loads(contents) or {}

    async def get(self, domain: str) -> dict[str, list[str]]:
        try:
            return await self._read_from_file(domain)
        except FileNotFoundError:
            return {}

    @staticmethod
    async def _write_to_file(domain: str, fields_to_selectors: dict[str, list[str]]) -> None:
        fields_to_selectors_unique = {field: list(set(selectors)) for field, selectors in fields_to_selectors.items()}

        async with aiofiles.open(f"_oxyparser_cache_{domain}", "w+") as file:
            await file.write(json.dumps(fields_to_selectors_unique))
            await file.write("\n")

    async def set(self, domain: str, fields_to_selectors: dict[str, list[str]]) -> None:
        try:
            current_cache = await self.get(domain)
        except FileNotFoundError:
            current_cache = {}

        if not current_cache:
            return await self._write_to_file(domain, fields_to_selectors)

        for field_name, selectors in fields_to_selectors.items():
            if field_name in current_cache:
                current_cache[field_name].extend(fields_to_selectors[field_name])
            else:
                current_cache[field_name] = fields_to_selectors[field_name]
        return await self._write_to_file(domain, current_cache)
