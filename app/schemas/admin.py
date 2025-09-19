from pydantic import BaseModel, EmailStr
from typing import Optional


# =====================
# Базовая схема
# =====================
class AdminBase(BaseModel):
    email: EmailStr
    role: str = "superadmin"   # "superadmin" | "owner"
    university_id: Optional[int] = None


# =====================
# Создание админа (POST)
# =====================
class AdminCreate(AdminBase):
    password: str   # пароль передаётся открытым текстом (захешируем потом)


# =====================
# Обновление админа (PUT / PATCH)
# =====================
class AdminUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    university_id: Optional[int] = None
    password: Optional[str] = None   # необязательное обновление пароля


# =====================
# Ответ (GET)
# =====================
class AdminOut(AdminBase):
    id: int

    class Config:
        orm_mode = True
