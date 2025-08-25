from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.user import UserUpdate
from app.dependencies import require_user

router = APIRouter(prefix="/users", tags=["users"])

@router.put("/me")
async def update_me(
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_user)
):
    current_user.first_name = user_data.first_name
    current_user.last_name = user_data.last_name
    await db.commit()
    return {"msg": "Profile updated"}
