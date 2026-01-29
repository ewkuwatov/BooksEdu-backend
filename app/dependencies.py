from fastapi import Depends, HTTPException, status, Cookie
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.models.user import User
from app.models.admin import Admin
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ---------- HELPERS ----------
async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if user:
        return user

    result = await db.execute(select(Admin).where(Admin.email == email))
    return result.scalars().first()


# ---------- CURRENT USER ----------
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        email = payload.get("sub")
        role = payload.get("role")

        if not email or not role:
            raise HTTPException(status_code=401, detail="Invalid token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # ADMIN / OWNER
    if role in ("owner", "superadmin"):
        result = await db.execute(
            select(Admin).where(Admin.email == email)
        )
        admin = result.scalars().first()
        if not admin:
            raise HTTPException(status_code=401, detail="Admin not found")
        return admin

    # USER
    result = await db.execute(
        select(User).where(User.email == email)
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User inactive")

    return user


# ---------- ROLES ----------
def require_role(roles: list[str]):
    async def checker(current_user=Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user

    return checker


# ✅ ВСЕ РОЛИ
require_user = require_role(["user", "owner", "superadmin"])
require_owner = require_role(["owner"])
require_owner_or_superadmin = require_role(["owner", "superadmin"])
