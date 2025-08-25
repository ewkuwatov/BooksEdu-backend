from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.direction import Direction
from app.schemas.direction import DirectionCreate, DirectionUpdate, DirectionOut
from app.dependencies import get_current_user

router = APIRouter(prefix="/directions", tags=["directions"])

# ---- Получение списка ----
@router.get("/", response_model=List[DirectionOut])
async def get_directions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Direction))
    return result.scalars().all()


# ---- Создание ---- (owner / superadmin)
@router.post("/", response_model=DirectionOut)
async def create_direction(
    data: DirectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # superadmin → автоматически подставляем свой университет
    if current_user.role == "superadmin":
        data.university_id = current_user.university_id

    # owner → должен явно указать university_id
    elif current_user.role == "owner":
        if not data.university_id:
            raise HTTPException(
                status_code=400,
                detail="Owner must specify university_id"
            )
    else:
        raise HTTPException(status_code=403, detail="Not allowed")

    # проверка уникальности course внутри конкретного университета
    result = await db.execute(
        select(Direction).where(
            Direction.course == data.course,
            Direction.university_id == data.university_id
        )
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=400,
            detail=f"Direction with course {data.course} already exists in this university"
        )

    direction = Direction(**data.model_dump())
    db.add(direction)
    await db.commit()
    await db.refresh(direction)
    return direction


# ---- Обновление ---- (owner / superadmin)
@router.put("/{direction_id}", response_model=DirectionOut)
async def update_direction(
    direction_id: int,
    data: DirectionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    direction = await db.get(Direction, direction_id)
    if not direction:
        raise HTTPException(status_code=404, detail="Direction not found")

    # superadmin → только свой универ
    if current_user.role == "superadmin" and direction.university_id != current_user.university_id:
        raise HTTPException(status_code=403, detail="Not your university")

    # owner → может обновлять любой
    if current_user.role not in ("owner", "superadmin"):
        raise HTTPException(status_code=403, detail="Not allowed")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(direction, field, value)

    await db.commit()
    await db.refresh(direction)
    return direction


# ---- Удаление ---- (owner / superadmin)
@router.delete("/{direction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_direction(
    direction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    direction = await db.get(Direction, direction_id)
    if not direction:
        raise HTTPException(status_code=404, detail="Direction not found")

    # superadmin → только свой универ
    if current_user.role == "superadmin" and direction.university_id != current_user.university_id:
        raise HTTPException(status_code=403, detail="Not your university")

    # owner → может удалять любой
    if current_user.role not in ("owner", "superadmin"):
        raise HTTPException(status_code=403, detail="Not allowed")

    await db.delete(direction)
    await db.commit()
    return None
