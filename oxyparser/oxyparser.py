from typing import Any, Literal, Type

import structlog
from pydantic import BaseModel, ValidationError
from tldextract import tldextract

from oxyparser.cache.base import BaseCache
from oxyparser.cache.file import FileCache
from oxyparser.cache.redis import RedisCache
from oxyparser.cache.utils import get_cache
from oxyparser.exceptions import ValidationException
from oxyparser.models import ParsedItem
from oxyparser.parser.ai_parser import AIParser
from oxyparser.scraper.scraper import Scraper

logger = structlog.get_logger()


class OxyParser:
    def __init__(self, cache_type: Literal["file", "redis"] | None = None):
        self.scraper: Scraper = Scraper()
        self.ai_parser: AIParser = AIParser()
        self.cache: FileCache | RedisCache | BaseCache = get_cache(cache_type) or BaseCache()

    @staticmethod
    def model_types_allowed(model: Type[BaseModel]) -> None:
        model_fields = model.model_fields
        for field, field_info in model_fields.items():
            if field_info.annotation not in [str, int]:
                raise ValidationException(
                    "OxyParser currently supports only simple schemas. "
                    "If you have a more complex schema, please create an issue on GitHub"
                )

    def _validate_model_types(self, model: Type[BaseModel]) -> None:
        self.model_types_allowed(model)

    @staticmethod
    def _validate_model_loads_correctly(model: Type[BaseModel], parsed_item: dict[str, Any]) -> BaseModel | None:
        try:
            return model(**parsed_item)
        except ValidationError:
            return None

    async def parse_with_cached_selectors(
        self, url: str, model: Type[BaseModel], html: str | None = None
    ) -> ParsedItem | None:
        if not self.cache:
            logger.debug("No cache selected for ", url=url)
            return None

        fields_to_selectors = await self.cache.get(tldextract.extract(url).domain)
        if not fields_to_selectors:
            logger.debug("No cached selectors for ", url=url)
            return None

        logger.debug("Using cached selectors for ", url=url)

        if html:
            return await self._parse_with_cached_selectors_html(url, model, fields_to_selectors, html)
        else:
            return await self._parse_with_cached_selectors_scraper(url, model, fields_to_selectors)

    async def _parse_with_cached_selectors_html(
        self,
        url: str,
        model: Type[BaseModel],
        fields_to_selectors: dict[str, list[str]],
        html: str,
    ) -> ParsedItem | None:
        parsed_item = self.ai_parser.parse_html(
            fields_to_selectors,
            self.ai_parser.split_body_into_parts(html),
        )
        return await self._validate_and_return_parsed_item(url, model, fields_to_selectors, parsed_item)

    async def _parse_with_cached_selectors_scraper(
        self,
        url: str,
        model: Type[BaseModel],
        fields_to_selectors: dict[str, list[str]],
    ) -> ParsedItem | None:
        parsed_item = await self.scraper.scrape_with_selectors(url, fields_to_selectors)
        return await self._validate_and_return_parsed_item(url, model, fields_to_selectors, parsed_item)

    async def _validate_and_return_parsed_item(
        self,
        url: str,
        model: Type[BaseModel],
        fields_to_selectors: dict[str, list[str]],
        parsed_item: Any,
    ) -> ParsedItem | None:
        loaded_model = self._validate_model_loads_correctly(model, parsed_item)
        if not loaded_model:
            logger.debug("Cached selectors are outdated for ", url=url)
            return None

        return ParsedItem(
            url=url,
            item=loaded_model,
            selectors=fields_to_selectors,
        )

    async def parse_with_ai_selectors(self, url: str, model: Type[BaseModel], html: str | None = None) -> ParsedItem:
        if not html:
            logger.info("Scraping ", url=url)
            html = await self.scraper.scrape(url)

        logger.info("Using AI parser for ", url=url)
        parsed_item = await self.ai_parser.parse(url, html, model)

        logger.info("Success! Returning parsed item for ", url=url)
        return parsed_item

    async def parse(self, url: str, model: Type[BaseModel], html: str | None = None) -> ParsedItem:
        self._validate_model_types(model)

        logger.debug("Starting OxyParser for ", url=url)

        parsed_item_from_cached_selectors = await self.parse_with_cached_selectors(url, model, html)
        if parsed_item_from_cached_selectors:
            logger.debug("Returning parsed item from cached selectors for ", url=url)
            return parsed_item_from_cached_selectors

        parsed_item = await self.parse_with_ai_selectors(url, model, html)
        logger.debug("Returning parsed item from AI selectors for ", url=url)

        logger.info("Saving selectors for ", url=url)
        await self.cache.set(tldextract.extract(url).domain, parsed_item.selectors)

        return parsed_item
