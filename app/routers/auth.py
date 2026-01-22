from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from sqlalchemy import select

from app.core.config import settings
from app.schemas.auth import UserRegister, UserLogin
from app.models.user import User
from app.models.admin import Admin
from app.db.session import get_db
from app.dependencies import get_user_by_email
from app.utils.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])


# ------------------------------
# Регистрация пользователя
# ------------------------------
@router.post("/register", response_model=dict)
async def register_user(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        hashed_password=hashed_password,
        role="user",
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"msg": "User registered", "user_id": new_user.id}


# ------------------------------
# Логин
# ------------------------------
@router.post("/login")
async def login(
    form_data: UserLogin,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    # 1️⃣ ищем в admins
    result = await db.execute(
        select(Admin).where(Admin.email == form_data.email)
    )
    account = result.scalar_one_or_none()
    account_type = "admin"

    # 2️⃣ если не нашли — ищем в users
    if not account:
        result = await db.execute(
            select(User).where(User.email == form_data.email)
        )
        account = result.scalar_one_or_none()
        account_type = "user"

    if not account or not verify_password(
        form_data.password, account.hashed_password
    ):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    role = getattr(account, "role", "user")
    university_id = getattr(account, "university_id", None)

    payload = {
        "sub": account.email,
        "role": role,
        "user_id": account.id,
        "university_id": university_id,
        "account_type": account_type,
        "type": "access",
    }

    access_token = create_access_token(payload)
    refresh_token = create_refresh_token({**payload, "type": "refresh"})

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        domain=".bookedu.uz",
        path="/",
        samesite="none",
        max_age=60 * 60 * 24 * 7,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": role,
        "email": account.email,
        "university_id": university_id,
        "account_type": account_type,
    }

# ------------------------------
# Логаут
# ------------------------------
@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(
    	key="refresh_token",
    	domain=".bookedu.uz",   # ← ВАЖНО
    	httponly=True,
    	secure=True,
    	samesite="none",
    )
    return {"msg": "Logged out"}


# ------------------------------
# Refresh
# ------------------------------
@router.post("/refresh")
async def refresh_token(response: Response, refresh_token: str = Cookie(None)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")

    try:
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        role = payload.get("role", "user")
        university_id = payload.get("university_id")

        new_access_token = create_access_token(
            {
                "sub": payload["sub"],
                "role": role,
                "user_id": payload["user_id"],
                "university_id": university_id,
                "type": "access",
            }
        )
        new_refresh_token = create_refresh_token(
            {
                "sub": payload["sub"],
                "role": role,
                "user_id": payload["user_id"],
                "university_id": university_id,
                "type": "refresh",
            }
        )

        # Обновляем refresh cookie
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=True,
            samesite="none",
	    domain=".bookedu.uz",
   	    path="/",
            max_age=60 * 60 * 24 * 7,
        )

        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "role": role,
            "email": payload["sub"],
            "university_id": university_id,
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
