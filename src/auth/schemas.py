from pydantic import BaseModel
from datetime import datetime


class PublicUrl(BaseModel):
    original_url: str
    short_url: str
    created_date: datetime
    expires_date: datetime
    click_count: int
    is_active: bool


class PrivateUrl(PublicUrl):
    id: int


class StatisticUrl(BaseModel):
    n_clicks: int
    status: bool


class ShortUrlRequest(BaseModel):
    original_url: str


class OriginalUrlRequest(BaseModel):
    short_url: str
