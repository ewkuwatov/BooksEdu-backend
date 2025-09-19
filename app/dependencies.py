from fastapi import Depends, HTTPException, status, Cookie
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.models.user import User
from app.models.admin import Admin
from app.core.config import settings

# ✅ объявляем здесь, а не в settings
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(Admin).where(Admin.email == email))
    admin = result.scalars().first()
    if admin:
        return admin
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def get_current_user(
    refresh_token: str = Cookie(None), db: AsyncSession = Depends(get_db)
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    try:
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    user = await get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    # Проверка только для User, а не Admin
    if isinstance(user, User) and not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive"
        )
    return user


async def get_current_admin(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),   # ✅ теперь используем наш локальный oauth2_scheme
) -> Admin:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        admin_id: int = payload.get("sub")
        if admin_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    query = await db.execute(select(Admin).where(Admin.id == admin_id))
    admin = query.scalar_one_or_none()
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin not found"
        )

    return admin


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
