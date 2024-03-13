import json
import os
import re
import time

import structlog
from litellm import acompletion
from openai import BadRequestError, RateLimitError
from tenacity import retry, stop_after_attempt, wait_exponential

from oxyparser.settings import settings

logger = structlog.get_logger()


os.environ["OPENAI_API_KEY"] = settings.LLM_API_KEY
os.environ["ANTHROPIC_API_KEY"] = settings.LLM_API_KEY


def extract_json_from_ai_response(response: str) -> dict[str, str]:
    pattern = r"{(.*?)}"
    matched_items = re.findall(pattern, response, re.DOTALL)
    item = "".join(matched_items)
    return json.loads(f"{{{item}}}") if item else {}


async def get_ai_response(prompt: dict[str, str]) -> dict[str, str]:
    messages = [
        {
            "role": "system",
            "content": "You are a senior developer who writes XPATHS to extract data from HTML. "
            "Please supplement the provided JSON object with an "
            "exact XPATH selector from the given HTML. "
            "You must always extract XPATH and never text. "
            "XPATHS must always end with //text(). Your output must be a valid JSON object",
        },
        {
            "role": "user",
            "content": f"JSON object should look like this and it should supplement the empty "
            f"selectors: f{prompt['json_schema']}",
        },
        {
            "role": "user",
            "content": f"Here is the HTML you need to parse: {prompt['html']}",
        },
    ]
    response = await acompletion(
        model=settings.LLM_MODEL,
        messages=messages,
        api_base=settings.LLM_API_BASE_URL,
        temperature=0,
    )
    content = response.model_dump()["choices"][0]["message"]["content"]
    logger.debug(f"Received AI content: {content}")

    json_response = extract_json_from_ai_response(content)
    return json_response


def generate_prompt(html: str, keys: list[str]) -> dict[str, str]:
    selector_schema = {key: "" for key in keys}

    return {"json_schema": json.dumps(selector_schema), "html": html}


@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
)
async def query_ai(prompt: dict[str, str]) -> dict[str, str]:
    now = time.time()

    try:
        response_content = await get_ai_response(prompt)
    except (json.decoder.JSONDecodeError, BadRequestError, RateLimitError) as exc:
        logger.error(exc, exc_info=True)
        return {"__error": str(exc)}
    logger.info(f"AI response time: {round(time.time() - now, 2)}")
    return response_content
