# schemas/kafedra.py
from pydantic import BaseModel
from typing import Optional

class KafedraBase(BaseModel):
    name: str

class KafedraCreate(KafedraBase):
    university_id: int

class KafedraUpdate(BaseModel):
    name: Optional[str] = None
    university_id: Optional[int] = None

class KafedraOut(KafedraBase):
    id: int
    university_id: int

    class Config:
        from_attributes = True
