from fastapi import Depends, HTTPException, status, Cookie
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.models.user import User
from app.models.admin import Admin
from app.core.config import settings

# access-токен всегда в Authorization: Bearer ...
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_user_by_email(db: AsyncSession, email: str):
    # Сначала ищем в users
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if user:
        return user

    # Потом ищем в admins
    result = await db.execute(select(Admin).where(Admin.email == email))
    return result.scalars().first()


# -------- ACCESS --------
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        role: str = payload.get("role")
        if not email or not role:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # 🔥 если admin / owner → ищем ТОЛЬКО в admins
    if role in ("owner", "superadmin", "admin"):
        result = await db.execute(select(Admin).where(Admin.email == email))
        admin = result.scalars().first()
        if not admin:
            raise HTTPException(status_code=401, detail="Admin not found")
        return admin

    # иначе → обычный user
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")

    return user

# -------- REFRESH --------
async def get_refresh_user(
    refresh_token: str = Cookie(None),
    db: AsyncSession = Depends(get_db),
):
    """Проверка refresh-токена (в cookie)"""
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token"
        )

    try:
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = await get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


# ---- Roles ----
def require_role(roles: list[str]):
    async def role_checker(current_user=Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
            )
        return current_user

    return role_checker


require_user = require_role(["user", "superadmin", "owner"])
require_superadmin = require_role(["superadmin", "owner"])
require_owner = require_role(["owner"])
require_owner_or_superadmin = require_role(["owner", "superadmin", "user"])
