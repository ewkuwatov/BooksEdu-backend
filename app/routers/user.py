from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.db.session import get_db
from app.schemas.user import UserUpdate, UserOut
from app.dependencies import require_user, require_owner
from sqlalchemy.future import select

router = APIRouter(prefix="/users", tags=["users"])

@router.put("/me")
async def update_me(
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_user)
):
    if user_data.first_name is not None:
        current_user.first_name = user_data.first_name
    if user_data.last_name is not None:
        current_user.last_name = user_data.last_name
    if user_data.email is not None:
        current_user.email = user_data.email
    if user_data.university_id is not None:
        current_user.university_id = user_data.university_id

    await db.commit()
    await db.refresh(current_user)
    return current_user

@router.put("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_owner),  # <-- только owner
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_data.first_name is not None:
        user.first_name = user_data.first_name
    if user_data.last_name is not None:
        user.last_name = user_data.last_name
    if user_data.email is not None:
        user.email = user_data.email
    if user_data.university_id is not None:
        user.university_id = user_data.university_id
    if user_data.is_active is not None:
        user.is_active = user_data.is_active  # блокировка

    await db.commit()
    await db.refresh(user)
    return user


# --- удалить пользователя (только owner) ---
@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_owner),  # <-- только owner
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()
    return {"msg": f"User {user_id} deleted"}


# --- заблокировать пользователя (owner) ---
@router.post("/{user_id}/block")
async def block_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_owner),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    await db.commit()
    return {"msg": f"User {user_id} blocked"}