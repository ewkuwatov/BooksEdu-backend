from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.analysis.literature_reports import LiteratureReport
from app.models.university import University
from app.schemas.analysis.literature_reports import (
    LiteratureCreate,
    LiteratureUpdate,
    LiteratureResponse,
)
from app.dependencies import get_current_admin

router = APIRouter(
    prefix="/literature-reports",
    tags=["Literature Reports"]
)

@router.post("/", response_model=LiteratureResponse)
async def create_literature(
    data: LiteratureCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    # 🔐 superadmin — только свой университет
    if current_user.role == "superadmin":
        if data.university_id != current_user.university_id:
            raise HTTPException(
                status_code=403,
                detail="You can only manage your own university"
            )

    result = await db.execute(
        select(University).where(University.id == data.university_id)
    )
    university = result.scalar_one_or_none()

    if not university:
        raise HTTPException(status_code=404, detail="University not found")

    record = LiteratureReport(**data.dict())
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return {
        **record.__dict__,
        "university_name": university.name
    }

@router.get("/", response_model=list[LiteratureResponse])
async def get_literature(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    query = select(LiteratureReport).join(University)

    if current_user.role == "superadmin":
        query = query.where(
            LiteratureReport.university_id == current_user.university_id
        )

    result = await db.execute(query)
    records = result.scalars().all()

    return [
        {
            **r.__dict__,
            "university_name": r.university.name
        }
        for r in records
    ]

@router.put("/{record_id}", response_model=LiteratureResponse)
async def update_literature(
    record_id: int,
    data: LiteratureUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    result = await db.execute(
        select(LiteratureReport).where(LiteratureReport.id == record_id)
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    if (
        current_user.role == "superadmin"
        and record.university_id != current_user.university_id
    ):
        raise HTTPException(
            status_code=403,
            detail="You can only edit your own university data"
        )

    for field, value in data.dict(exclude_unset=True).items():
        setattr(record, field, value)

    await db.commit()
    await db.refresh(record)

    return {
        **record.__dict__,
        "university_name": record.university.name
    }

@router.delete("/{record_id}")
async def delete_literature(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    result = await db.execute(
        select(LiteratureReport).where(LiteratureReport.id == record_id)
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    if (
        current_user.role == "superadmin"
        and record.university_id != current_user.university_id
    ):
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own university data"
        )

    await db.delete(record)
    await db.commit()

    return {"detail": "Deleted successfully"}
