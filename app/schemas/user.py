from pydantic import BaseModel, EmailStr, constr
from enum import Enum
from typing import Optional

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


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[constr(min_length=6)] = None


class UserOut(UserBase):
    id: int
    role: str

    class Config:
        orm_mode = True

class UserRead(UserBase):
    id: int
    university_id: Optional[int] = None
    class Config:
        orm_mode = True

