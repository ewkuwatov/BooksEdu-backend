from pydantic import BaseModel, EmailStr, constr
from enum import Enum
from typing import Optional

from app.schemas.university import UniversityOut


class RoleEnum(str, Enum):
    superadmin = "superadmin"
    user = "user"
    owner = "owner"

class UserLogin(BaseModel):
    email: EmailStr
    password: constr(min_length=6)

class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


class UserCreate(UserBase):
    password: constr(min_length=6)
    university_id: Optional[int] = None


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[constr(min_length=6)] = None
    university_id: Optional[int] = None
    is_active: Optional[bool] = None

class UserOut(UserBase):
    id: int
    role: str
    university: Optional[UniversityOut] = None

    class Config:
        from_attributes = True

class UserRead(UserBase):
    id: int
    university_id: Optional[int] = None

    class Config:
        from_attributes = True
