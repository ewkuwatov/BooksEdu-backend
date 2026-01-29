from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.university import University
from app.schemas.university import (
    UniversityCreate,
    UniversityUpdate,
    UniversityOut,
)
from app.db.session import get_db
from app.dependencies import require_owner, require_owner_or_superadmin

router = APIRouter(prefix="/universities", tags=["universities"])


# ---------- GET ALL ----------
@router.get("/", response_model=List[UniversityOut])
async def get_universities(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(University))
    return result.scalars().all()


# ---------- GET ONE ----------
@router.get("/{uni_id}", response_model=UniversityOut)
async def get_university(
    uni_id: int,
    db: AsyncSession = Depends(get_db),
):
    uni = await db.get(University, uni_id)
    if not uni:
        raise HTTPException(status_code=404, detail="University not found")
    return uni


# ---------- CREATE ----------
@router.post("/", response_model=UniversityOut)
async def create_university(
    uni_data: UniversityCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_owner),
):
    new_uni = University(**uni_data.model_dump())
    db.add(new_uni)
    await db.commit()
    await db.refresh(new_uni)
    return new_uni


# ---------- UPDATE ----------
@router.put("/{uni_id}", response_model=UniversityOut)
async def update_university(
    uni_id: int,
    uni_data: UniversityUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_owner_or_superadmin),
):
    uni = await db.get(University, uni_id)
    if not uni:
        raise HTTPException(status_code=404, detail="University not found")

    for field, value in uni_data.model_dump(exclude_unset=True).items():
        setattr(uni, field, value)

    await db.commit()
    await db.refresh(uni)
    return uni


# ---------- DELETE ----------
@router.delete("/{uni_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_university(
    uni_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_owner),
):
    uni = await db.get(University, uni_id)
    if not uni:
        raise HTTPException(status_code=404, detail="University not found")

    await db.delete(uni)
    await db.commit()
