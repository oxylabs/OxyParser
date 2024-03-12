import abc
import re
from typing import Any, Type

import lxml
import structlog
from lxml import html
from pydantic import BaseModel

from oxyparser.exceptions import EmptyBodyException
from oxyparser.models import ParsedItem
from oxyparser.parser.cleaner import clean_html
from oxyparser.settings import settings
from oxyparser.utils import get_token_count

logger = structlog.get_logger()


class Parser:
    @staticmethod
    def split_body_into_parts(cleaned_body: str) -> list[str]:
        """
        Breaks cleaned body into chunks, so we can pass it to OpenAI api instead of passing the whole body
        which may sometimes be too large
        :param cleaned_body: html body to split
        :return:
        """
        clean_body_token_count = get_token_count(cleaned_body)
        bodies = [cleaned_body]
        if clean_body_token_count >= settings.MAX_TOKEN_COUNT:
            chunk_size = settings.MAX_TOKEN_COUNT * 4
            while True:
                body_chunks = [cleaned_body[i : i + chunk_size] for i in range(0, len(cleaned_body), chunk_size)]
                token_counts = [get_token_count(body_chunk) for body_chunk in body_chunks]
                if max(token_counts) < settings.MAX_TOKEN_COUNT:
                    bodies = body_chunks
                    break
                chunk_size -= 5000
        return bodies

    @staticmethod
    def modify_class_selector(selector: str) -> str | None:
        """
        Modify class selector to be used in xpath. OpenAI sometimes returns classes which can only be found
        using contains() function in xpath
        """
        regex_pattern = r"\[@class='([^']+)'\]"
        matches = re.findall(regex_pattern, selector)
        if matches:
            selector_class = matches[0]
            selector = selector.replace(f"[@class='{matches[0]}']", f"[contains(@class, '{selector_class}')]")
            return selector
        return None

    def get_data(self, html_elem: lxml.html, selector: str) -> list[str]:
        modifiers = [self.modify_class_selector]

        data = html_elem.xpath(selector)
        for modifier in modifiers:
            modified_selector = modifier(selector)
            if not modified_selector:
                continue
            data = html_elem.xpath(modified_selector)
            if data:
                break
        return data

    @staticmethod
    def modify_selector_to_grab_text(selector: str) -> str:
        """
        Modify selector to grab text correctly. OpenAI sometimes doesn't return the text selector correctly, so
        we fix it ourselves
        """
        if selector.endswith("/text()") and "//text()" not in selector:
            selector = selector.replace("/text()", "//text()")
        if not selector.endswith("//text()"):
            selector = f"{selector}//text()"
        return selector

    def parse_html(self, field_to_selectors: dict[str, list[str]], cleaned_body_in_parts: list[str]) -> dict[str, Any]:
        body = "".join(cleaned_body_in_parts)
        html_elem = html.fromstring(body)

        parsed_body: dict[str, Any] = {}

        for key, selectors in field_to_selectors.items():
            logger.info(f"parsing {key=} which has {len(selectors)} selectors")

            for selector in selectors:
                if not selector:
                    continue

                selector = self.modify_selector_to_grab_text(selector)

                try:
                    data = self.get_data(html_elem, selector)
                except lxml.etree.XPathEvalError:
                    logger.error(f"Error parsing {key=} | {selector=}")
                    parsed_body[key] = None
                    continue

                logger.debug(f"{key=} | {selector=}")
                if not data:
                    logger.info(f"Empty data for {key=} | {selector=}")
                    parsed_body[key] = None
                    continue

                items = [item.strip() for item in data if item]
                parsed_body[key] = items
                logger.debug(f"data: {items}")
                break

        return parsed_body

    @staticmethod
    def _get_fields(model: Type[BaseModel]) -> list[str]:
        model_fields = model.model_fields.keys()
        return list(model_fields)

    @staticmethod
    def _get_missing_fields(model: Type[BaseModel], item: dict[str, Any]) -> list[str]:
        model_fields = model.model_fields
        missing_fields = []
        for field, field_info in model_fields.items():
            if not item.get(field) and bool(field_info.is_required):
                missing_fields.append(field)
        return missing_fields

    @staticmethod
    def _join_item(item_raw: dict[str, list[str]]) -> dict[str, Any]:
        return {key: " ".join(val for val in values) if values else None for key, values in item_raw.items()}

    async def parse(self, url: str, body: str, model: Type[BaseModel]) -> ParsedItem:
        cleaned_body = clean_html(body)
        if not cleaned_body:
            raise EmptyBodyException(f"Body is empty for {url}")

        cleaned_body_in_parts = self.split_body_into_parts(cleaned_body)
        fields = self._get_fields(model)
        field_to_selectors = await self.get_selectors(fields, cleaned_body_in_parts)

        parsed_item_raw = self.parse_html(field_to_selectors, cleaned_body_in_parts)
        item = self._join_item(parsed_item_raw)

        missing_fields = self._get_missing_fields(model, item)
        for field in missing_fields:
            missing_fields_to_selectors = await self.get_selectors([field], cleaned_body_in_parts)
            parsed_item_missing_selectors = self.parse_html(missing_fields_to_selectors, cleaned_body_in_parts)
            item_missing_selectors = self._join_item(parsed_item_missing_selectors)
            item[field] = item_missing_selectors[field]

        return ParsedItem(url=url, item=model(**item), selectors=field_to_selectors)

    @abc.abstractmethod
    async def get_selectors(self, fields: list[str], cleaned_body_in_parts: list[str]) -> dict[str, list[str]]: ...
