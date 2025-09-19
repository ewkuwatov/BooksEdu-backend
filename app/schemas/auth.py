from typing import Optional
from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    role: str = "user"

class AdminCreate(BaseModel):
    email: EmailStr
    password: str
    university_id: int

class UserLogin(BaseModel):
    email: EmailStr
    password: str
