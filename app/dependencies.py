from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.models.user import User
from app.models.admin import Admin
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# ================== helpers ===================
async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(Admin).where(Admin.email == email))
    admin = result.scalars().first()
    if admin:
        return admin

    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()

# ================== auth ===================
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user_by_email(db, email)
    if not user:
        raise credentials_exception

    return user

# ================== roles ===================
def require_role(roles: list[str]):
    async def role_checker(current_user=Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker

async def require_owner_or_superadmin(
    current_user=Depends(get_current_user)
):
    if current_user.role not in ("owner", "superadmin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

require_user = require_role(["user", "superadmin", "owner"])
require_superadmin = require_role(["superadmin", "owner"])
require_owner = require_role(["owner"])
