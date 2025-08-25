# schemas/direction.py
from pydantic import BaseModel
from typing import Optional

class DirectionBase(BaseModel):
    number: str
    name: str
    course: int
    student_count: int

class DirectionCreate(DirectionBase):
    university_id: int

class DirectionUpdate(BaseModel):
    number: Optional[str] = None
    name: Optional[str] = None
    course: Optional[int] = None
    student_count: Optional[int] = None
    university_id: Optional[int] = None

class DirectionOut(DirectionBase):
    id: int
    university_id: int

    class Config:
        from_attributes = True
