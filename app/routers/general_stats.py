# app/routers/general_stats.py
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.university import University
from app.models.direction import Direction

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/general")
async def general_stats(
    db: AsyncSession = Depends(get_db),
):
    # Общее количество университетов
    uni_result = await db.execute(
        select(func.count(University.id))
    )
    total_universities = uni_result.scalar() or 0

    # Общее количество студентов (сумма всех student_count в directions)
    student_result = await db.execute(
        select(func.coalesce(func.sum(Direction.student_count), 0))
    )
    total_students = student_result.scalar() or 0

    # Общее количество направлений
    direction_result = await db.execute(
        select(func.count(Direction.id))
    )
    total_directions = direction_result.scalar() or 0

    return {
        "total_universities": total_universities,
        "total_students": total_students,
        "total_directions": total_directions
    }
