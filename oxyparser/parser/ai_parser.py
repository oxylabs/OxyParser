import json
from collections import defaultdict

import structlog

from oxyparser.ai.query import generate_prompt, query_ai
from oxyparser.parser.parser import Parser
from oxyparser.settings import settings
from oxyparser.utils import get_token_count

logger = structlog.get_logger()


class AIParser(Parser):
    @staticmethod
    async def call_ai_for_selectors(fields: list[str], cleaned_body_in_parts: list[str]) -> dict[str, list[str]]:
        field_to_selectors = defaultdict(list)

        for index, cleaned_body_part in enumerate(cleaned_body_in_parts):
            part = index + 1
            logger.info(f"Part {part}/{len(cleaned_body_in_parts)} getting selectors for url")
            prompt = generate_prompt(cleaned_body_part, fields)
            prompt_token_count = get_token_count(json.dumps(prompt))
            logger.info(f"Prompt generated, token count: {prompt_token_count}")
            selectors = await query_ai(prompt)
            error = selectors.get("__error")
            if error:
                logger.info(f"Error from LLM({settings.LLM_MODEL}): {error} skipping this part {part}")
                continue

            for data_key, selector in selectors.items():
                field_to_selectors[data_key].append(selector)

        return field_to_selectors

    async def get_selectors(self, fields: list[str], cleaned_body_in_parts: list[str]) -> dict[str, list[str]]:
        return await self.call_ai_for_selectors(fields, cleaned_body_in_parts)

    async def get_missing_selectors(
        self, missing_fields: list[str], cleaned_body_in_parts: list[str]
    ) -> defaultdict[str, list[list[str]]]:
        field_to_selectors = defaultdict(list)
        for field in missing_fields:
            selectors = await self.call_ai_for_selectors([field], cleaned_body_in_parts)
            field_to_selectors[field].append(selectors[field])
        return field_to_selectors
