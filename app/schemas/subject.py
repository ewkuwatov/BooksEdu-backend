from pydantic import BaseModel
from typing import Optional, List

class SubjectBase(BaseModel):
    name: str
    kafedra_id: int

class SubjectCreate(SubjectBase):
    direction_ids: List[int]
    university_id: int

class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    kafedra_id: Optional[int] = None
    direction_ids: Optional[List[int]] = None
    university_id: Optional[int] = None

class SubjectOut(SubjectBase):
    id: int
    university_id: int
    direction_ids: List[int] = []

    class Config:
        from_attributes = True
