from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.university import University
from app.schemas.university import UniversityCreate, UniversityOut, UniversityUpdate
from app.db.session import get_db
from app.dependencies import get_current_user, require_owner_or_superadmin

router = APIRouter(prefix="/universities", tags=["universities"])


# ---- Получение списка ----
@router.get("/", response_model=List[UniversityOut])
async def get_universities(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(University))
    return result.scalars().all()

@router.get("/{uni_id}", response_model=UniversityOut)
async def get_university(
    uni_id: int,
    db: AsyncSession = Depends(get_db),
):
    uni = await db.get(University, uni_id)
    if not uni:
        raise HTTPException(status_code=404, detail="University not found")
    return uni

# ---- Создание ---- (только owner)
@router.post("/", response_model=UniversityOut)
async def create_university(
    uni_data: UniversityCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Only owners can create universities")

    new_uni = University(**uni_data.model_dump())  # pydantic v2
    db.add(new_uni)
    await db.commit()
    await db.refresh(new_uni)
    return new_uni


# ---- Обновление ---- (owner → любой, superadmin → только свой)
@router.put("/{uni_id}", response_model=UniversityOut)
async def update_university(
    uni_id: int,
    uni_data: UniversityUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_owner_or_superadmin)
):
    uni = await db.get(University, uni_id)
    if not uni:
        raise HTTPException(status_code=404, detail="University not found")

    if current_user.role == "superadmin" and current_user.university_id != uni_id:
        raise HTTPException(status_code=403, detail="Not your university")

    for field, value in uni_data.model_dump(exclude_unset=True).items():
        setattr(uni, field, value)

    await db.commit()
    await db.refresh(uni)
    return uni


# ---- Удаление ---- (только owner)
@router.delete("/{uni_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_university(
    uni_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Only owners can delete universities")

    uni = await db.get(University, uni_id)
    if not uni:
        raise HTTPException(status_code=404, detail="University not found")

    await db.delete(uni)
    await db.commit()
