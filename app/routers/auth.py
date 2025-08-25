from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.schemas.auth import UserRegister, AdminCreate, Token, TokenPair, RefreshRequest
from app.schemas.user import UserLogin
from app.models.user import User
from app.models.admin import Admin
from app.db.session import get_db
from app.dependencies import require_role
from app.utils.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from jose import jwt, JWTError

router = APIRouter(prefix="/auth", tags=["auth"])


# ------------------------------
# Вспомогательная функция
# ------------------------------
async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if user:
        return user

    result = await db.execute(select(Admin).where(Admin.email == email))
    return result.scalars().first()


# ------------------------------
# Регистрация обычного пользователя (любой)
# ------------------------------
@router.post("/register", response_model=dict)
async def register_user(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    # Проверяем, есть ли уже такой email
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,  # <-- исправил баг (у тебя было 2 раза first_name)
        email=user_data.email,
        hashed_password=hashed_password,
        role="user"
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"msg": "User registered", "user_id": new_user.id}



# ------------------------------
# Создание админов (только owner)
# ------------------------------
@router.post("/create-admin", response_model=dict)
async def create_admin(
    user_data: AdminCreate,
    db: AsyncSession = Depends(get_db),
    current_owner: Admin = Depends(require_role("owner"))  # ✅ проверка роли
):
    hashed_password = get_password_hash(user_data.password)
    new_admin = Admin(
        email=user_data.email,
        hashed_password=hashed_password,
        role="superadmin",
        university_id=user_data.university_id
    )
    db.add(new_admin)
    await db.commit()
    await db.refresh(new_admin)
    return {
        "msg": "Superadmin created",
        "id": new_admin.id,
        "university_id": new_admin.university_id
    }


# ------------------------------
# Логин (любой)
# ------------------------------
@router.post("/login", response_model=TokenPair)
async def login(form_data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == form_data.email))
    user = result.scalars().first()

    if not user:
        result = await db.execute(select(Admin).where(Admin.email == form_data.email))
        user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    role = getattr(user, "role", "user")

    access_token = create_access_token(
        data={"sub": user.email, "role": role, "user_id": user.id}
    )
    refresh_token = create_refresh_token({"sub": user.email, "role": role, "user_id": user.id})

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/refresh", response_model=TokenPair)
async def refresh_token(request: RefreshRequest):
    try:
        payload = jwt.decode(request.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        new_access_token = create_access_token({
            "sub": payload["sub"],
            "role": payload["role"],
            "user_id": payload["user_id"]
        })
        new_refresh_token = create_refresh_token({
            "sub": payload["sub"],
            "role": payload["role"],
            "user_id": payload["user_id"]
        })
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")