from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

from app.schemas.tag import TagOut


class NewsBase(BaseModel):
    title: str
    description: str
    img: Optional[str] = None


class NewsCreate(NewsBase):
    university_id: Optional[int] = None  # superadmin → подставляем сами, owner → может выбрать
    tags: List[str] = []

class NewsUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    img: Optional[str] = None
    tags: Optional[List[str]] = None

class NewsOut(NewsBase):
    id: int
    date: datetime
    university_id: int

    class Config:
        from_attributes = True
