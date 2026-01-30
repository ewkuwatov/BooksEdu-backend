from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.analysis.library_fund import LibraryFund
from app.models.university import University
from app.schemas.analysis.library_fund import (
    LibraryFundCreate,
    LibraryFundUpdate,   # ← ВОТ ЭТОГО НЕ ХВАТАЛО
    LibraryFundResponse
)
from app.dependencies import get_current_admin

router = APIRouter(
    prefix="/library-fund",
    tags=["Library Fund"]
)

@router.post("/", response_model=LibraryFundResponse)
async def create_library_fund(
    data: LibraryFundCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    # 🔒 superadmin может писать ТОЛЬКО в свой университет
    if current_user.role == "superadmin":
        if data.university_id != current_user.university_id:
            raise HTTPException(
                status_code=403,
                detail="You can only manage your own university"
            )

    # Проверка университета
    result = await db.execute(
        select(University).where(University.id == data.university_id)
    )
    university = result.scalar_one_or_none()

    if not university:
        raise HTTPException(status_code=404, detail="University not found")

    fund = LibraryFund(**data.dict())
    db.add(fund)
    await db.commit()
    await db.refresh(fund)

    return {
        **fund.__dict__,
        "university_name": university.name
    }



@router.get("/", response_model=list[LibraryFundResponse])
async def get_library_funds(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    query = select(LibraryFund).join(University)

    # 🔐 superadmin — только свой универ
    if current_user.role == "superadmin":
        query = query.where(
            LibraryFund.university_id == current_user.university_id
        )

    result = await db.execute(query)
    funds = result.scalars().all()

    return [
        {
            "id": f.id,
            "university_id": f.university_id,
            "university_name": f.university.name,

            "arm_fond_nomi": f.arm_fond_nomi,
            "arm_fond_nusxada": f.arm_fond_nusxada,

            "uz_kiril": f.uz_kiril,
            "uz_lotin": f.uz_lotin,
            "rus": f.rus,
            "ingliz": f.ingliz,
            "boshqa_tillar": f.boshqa_tillar,

            "bosma": f.bosma,
            "elektron": f.elektron,
            "brayl": f.brayl,
            "audio": f.audio,

            "oquv_adabiyot": f.oquv_adabiyot,
            "ilmiy_adabiyot": f.ilmiy_adabiyot,
            "badiiy_adabiyot": f.badiiy_adabiyot,
            "xorijiy_adabiyot": f.xorijiy_adabiyot,
            "boshqa_adabiyot": f.boshqa_adabiyot,
        }
        for f in funds
    ]

@router.put("/{fund_id}", response_model=LibraryFundResponse)
async def update_library_fund(
    fund_id: int,
    data: LibraryFundUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    result = await db.execute(
        select(LibraryFund).where(LibraryFund.id == fund_id)
    )
    fund = result.scalar_one_or_none()

    if not fund:
        raise HTTPException(status_code=404, detail="Record not found")

    # 🔐 superadmin может менять ТОЛЬКО свой университет
    if (
        current_user.role == "superadmin"
        and fund.university_id != current_user.university_id
    ):
        raise HTTPException(
            status_code=403,
            detail="You can only edit your own university data"
        )

    # обновляем только переданные поля
    for field, value in data.dict(exclude_unset=True).items():
        setattr(fund, field, value)

    await db.commit()
    await db.refresh(fund)

    return {
        **fund.__dict__,
        "university_name": fund.university.name
    }

@router.delete("/{fund_id}")
async def delete_library_fund(
    fund_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    result = await db.execute(
        select(LibraryFund).where(LibraryFund.id == fund_id)
    )
    fund = result.scalar_one_or_none()

    if not fund:
        raise HTTPException(status_code=404, detail="Record not found")

    # 🔐 доступ
    if (
        current_user.role == "superadmin"
        and fund.university_id != current_user.university_id
    ):
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own university data"
        )

    await db.delete(fund)
    await db.commit()

    return {"detail": "Deleted successfully"}
