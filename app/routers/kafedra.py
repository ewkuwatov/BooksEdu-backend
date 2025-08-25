from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.kafedra import Kafedra
from app.schemas.kafedra import KafedraCreate, KafedraUpdate, KafedraOut
from app.dependencies import get_current_user

router = APIRouter(prefix="/kafedras", tags=["kafedras"])


# ---- Получение списка ----
@router.get("/", response_model=List[KafedraOut])
async def get_kafedras(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Kafedra))
    return result.scalars().all()


# ---- Создание ---- (owner / superadmin)
@router.post("/", response_model=KafedraOut)
async def create_kafedra(
    data: KafedraCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role == "superadmin":
        data.university_id = current_user.university_id
    elif current_user.role == "owner":
        if not data.university_id:
            raise HTTPException(
                status_code=400,
                detail="university_id is required for owner"
            )
    else:
        raise HTTPException(status_code=403, detail="Not allowed")

    kafedra = Kafedra(**data.model_dump())
    db.add(kafedra)
    await db.commit()
    await db.refresh(kafedra)
    return kafedra


# ---- Обновление ---- (owner / superadmin)
@router.put("/{kafedra_id}", response_model=KafedraOut)
async def update_kafedra(
    kafedra_id: int,
    data: KafedraUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    kafedra = await db.get(Kafedra, kafedra_id)
    if not kafedra:
        raise HTTPException(status_code=404, detail="Kafedra not found")

    if current_user.role == "superadmin" and kafedra.university_id != current_user.university_id:
        raise HTTPException(status_code=403, detail="Not your university")

    if current_user.role not in ("owner", "superadmin"):
        raise HTTPException(status_code=403, detail="Not allowed")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(kafedra, field, value)

    await db.commit()
    await db.refresh(kafedra)
    return kafedra

# ---- Удаление ---- (owner / superadmin)
@router.delete("/{kafedra_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_kafedra(
    kafedra_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    kafedra = await db.get(Kafedra, kafedra_id)
    if not kafedra:
        raise HTTPException(status_code=404, detail="Kafedra not found")

    # superadmin → только свой универ
    if current_user.role == "superadmin" and kafedra.university_id != current_user.university_id:
        raise HTTPException(status_code=403, detail="Not your university")

    # owner → может удалять любой
    if current_user.role not in ("owner", "superadmin"):
        raise HTTPException(status_code=403, detail="Not allowed")

    await db.delete(kafedra)
    await db.commit()
    return None

