# schemas/literature.py
from pydantic import BaseModel
from typing import Optional


class LiteratureBase(BaseModel):
    title: str
    kind: str
    author: Optional[str] = None
    publisher: Optional[str] = None
    language: str
    font_type: str
    condition: str
    usage_status: str
    year: int
    printed_count: Optional[int] = None
    image: Optional[str] = None
    file_path: Optional[str] = None


class LiteratureCreate(LiteratureBase):
    subject_id: int
    university_id: int


class LiteratureUpdate(BaseModel):
    title: Optional[str] = None
    kind: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    language: Optional[str] = None
    font_type: Optional[str] = None
    condition: Optional[str] = None
    usage_status: Optional[str] = None

    year: Optional[int] = None
    printed_count: Optional[int] = None
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

