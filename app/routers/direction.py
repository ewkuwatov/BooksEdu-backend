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

    # ✅ проверка уникальности комбинации внутри университета
    result = await db.execute(
        select(Direction).where(
            Direction.university_id == data.university_id,
            Direction.number == data.number,
            Direction.name == data.name,
            Direction.course == data.course
        )
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=400,
            detail="Direction with this number, name and course already exists in this university"
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

    # ✅ преобразуем данные обновления
    update_data = data.model_dump(exclude_unset=True)

    # получаем новые значения (если переданы)
    new_number = update_data.get("number", direction.number)
    new_name = update_data.get("name", direction.name)
    new_course = update_data.get("course", direction.course)
    new_university_id = update_data.get("university_id", direction.university_id)

    # ✅ проверка уникальности новой комбинации
    result = await db.execute(
        select(Direction).where(
            Direction.id != direction_id,
            Direction.university_id == new_university_id,
            Direction.number == new_number,
            Direction.name == new_name,
            Direction.course == new_course
        )
    )

    if result.scalars().first():
        raise HTTPException(
            status_code=400,
            detail="Direction with this number, name and course already exists in this university"
        )

    # ✅ применяем изменения
    for field, value in update_data.items():
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
