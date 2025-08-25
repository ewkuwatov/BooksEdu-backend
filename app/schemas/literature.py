# schemas/literature.py
from pydantic import BaseModel
from typing import Optional
from app.schemas.enums import LanguageEnum, FontTypeEnum, ConditionEnum, UsageStatusEnum

class LiteratureBase(BaseModel):
    title: str
    kind: str
    author: Optional[str] = None
    publisher: Optional[str] = None
    language: LanguageEnum
    font_type: FontTypeEnum
    year: int
    printed_count: Optional[int] = None
    condition: ConditionEnum
    usage_status: UsageStatusEnum
    image: Optional[str] = None
    file_path: Optional[str] = None

class LiteratureCreate(LiteratureBase):
    subject_id: int

class LiteratureUpdate(BaseModel):
    title: Optional[str] = None
    kind: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    language: Optional[LanguageEnum] = None
    font_type: Optional[FontTypeEnum] = None
    year: Optional[int] = None
    printed_count: Optional[int] = None
    condition: Optional[ConditionEnum] = None
    usage_status: Optional[UsageStatusEnum] = None
    image: Optional[str] = None
    file_path: Optional[str] = None
    subject_id: Optional[int] = None
    university_id: Optional[int] = None

class LiteratureOut(LiteratureBase):
    id: int
    subject_id: int
    university_id: int

    class Config:
        from_attributes = True
