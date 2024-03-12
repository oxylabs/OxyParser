import os

import pytest
from pydantic import BaseModel

from oxyparser.oxyparser import OxyParser


class ExampleModel(BaseModel):
    name: str
    surname: str
    address: str
    age: str


html = (
    "<html><body>" "<h1>John</h1>" "<h2>Smith</h2>" "<p>Svitrigailos st.</p>" "<span>2 years old</span></body></html>"
)
IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"


@pytest.mark.skipif(IN_GITHUB_ACTIONS, reason="Test doesn't work in Github Actions.")
@pytest.mark.asyncio
async def test_it_parses_html_with_cached_selectors_correctly() -> None:
    parser = OxyParser(cache_type="file")

    url = "https://example.com"
    parsed_item = await parser.parse(url=url, model=ExampleModel, html=html)

    job_item = ExampleModel(**parsed_item.item.model_dump())
    assert job_item.name == "John"
    assert job_item.surname == "Smith"
    assert job_item.address == "Svitrigailos st."
    assert job_item.age == "2 years old"


@pytest.mark.skipif(IN_GITHUB_ACTIONS, reason="Test doesn't work in Github Actions.")
@pytest.mark.asyncio
async def test_it_parses_html_with_ai_parser_correctly() -> None:
    parser = OxyParser()

    url = "https://humans.com"
    parsed_item = await parser.parse(url=url, model=ExampleModel, html=html)

    job_item = ExampleModel(**parsed_item.item.model_dump())
    assert job_item.name == "John"
    assert job_item.surname == "Smith"
    assert job_item.address == "Svitrigailos st."
    assert job_item.age == "2 years old"
