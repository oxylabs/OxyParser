from datetime import datetime

from pydantic import BaseModel


class ParsedItem(BaseModel):
    url: str
    item: BaseModel
    selectors: dict[str, list[str]]
    date: datetime = datetime.now()


class Field(BaseModel):
    key: str
    is_required: bool
