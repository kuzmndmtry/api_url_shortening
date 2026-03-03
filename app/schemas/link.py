from typing import Optional

from pydantic import BaseModel, HttpUrl
from datetime import datetime

class LinkCreate(BaseModel):
    original_url: HttpUrl
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = None

class LinkResponse(BaseModel):
    id: int
    original_url: str
    short_code: str
    created_date: datetime

    class Config:
        from_attributes = True