from typing import Any, Sequence

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from oxyparser.exceptions import FailedOxylabsRequestException
from oxyparser.settings import settings


class Scraper:
    @staticmethod
    def build_parsing_instructions(
        fields_to_xpaths: dict[str, list[str]],
    ) -> dict[str, dict[str, list[dict[str, Sequence[str]]]]]:
        """
        https://developers.oxylabs.io/scraper-apis/custom-parser/parsing-instruction-examples
        :param fields_to_xpaths: fields and their respective selectors retrieved by AI
        :return:
        """
        parsing_instructions = {}

        for field, xpaths in fields_to_xpaths.items():
            parsing_instructions[field] = {"_fns": [{"_fn": "xpath_one", "_args": xpaths}]}
        return parsing_instructions

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
    )
    async def scrape_with_selectors(self, url: str, fields_to_xpaths: dict[str, list[str]]) -> dict[str, Any]:
        payload = {
            "source": "universal",
            "url": url,
            "render": "html",
            "parsing_instructions": self.build_parsing_instructions(fields_to_xpaths),
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.OXYLABS_SCRAPER_HOST,
                json=payload,
                auth=(settings.OXYLABS_SCRAPER_USER, settings.OXYLABS_SCRAPER_PASSWORD),
                timeout=settings.OXYLABS_SCRAPER_TIMEOUT,
            )
            if response.status_code != 200:
                raise FailedOxylabsRequestException(f"Failed to scrape {url}, check your keys...")
            response_json = response.json()
            content = response_json["results"][0]["content"]
            return content

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
    )
    async def scrape(self, url: str) -> str:
        """
        For detailed usage, please refer to:

        https://developers.oxylabs.io/scraper-apis/web-scraper-api

        Scrapes given URL and returns it's HTML as string
        :param url: URL to scrape
        :return:
        """
        payload = {
            "source": "universal",
            "url": url,
            "render": "html",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.OXYLABS_SCRAPER_HOST,
                json=payload,
                auth=(settings.OXYLABS_SCRAPER_USER, settings.OXYLABS_SCRAPER_PASSWORD),
                timeout=settings.OXYLABS_SCRAPER_TIMEOUT,
            )
            if response.status_code != 200:
                raise FailedOxylabsRequestException(f"Failed to scrape {url}, check your keys...")
            response_json = response.json()
            content = response_json["results"][0]["content"]
            return content
