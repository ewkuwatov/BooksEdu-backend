# app/routers/owner_stats.py
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.university import University
from app.models.direction import Direction
from app.models.subject import Subject
from app.models.literature import Literature
from app.dependencies import get_current_user

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/owner-universities")
async def owner_universities_stats(
        db: AsyncSession = Depends(get_db),
        current_user=Depends(get_current_user)
):
    # Ограничиваем доступ только для owner или superadmin
    if current_user.role not in ("owner", "superadmin"):
        return {"detail": "Not allowed"}

    # Получаем список университетов в зависимости от роли
    if current_user.role == "superadmin":
        result = await db.execute(
            select(University).where(University.id == current_user.university_id)
        )
    else:  # owner
        result = await db.execute(select(University))

    universities = result.scalars().all()
    stats_list = []

    for uni in universities:
        # Сумма всех студентов по направлениям
        student_result = await db.execute(
            select(func.coalesce(func.sum(Direction.student_count), 0))
            .where(Direction.university_id == uni.id)
        )
        total_students = student_result.scalar() or 0

        # Количество направлений
        direction_result = await db.execute(
            select(func.count(Direction.id))
            .where(Direction.university_id == uni.id)
        )
        total_directions = direction_result.scalar() or 0

        # Количество предметов
        subject_result = await db.execute(
            select(func.count(Subject.id))
            .where(Subject.university_id == uni.id)
        )
        total_subjects = subject_result.scalar() or 0

        # Количество литературы
        literature_result = await db.execute(
            select(func.count(Literature.id))
            .where(Literature.university_id == uni.id)
        )
        total_literature = literature_result.scalar() or 0

        # Расчет процента доступной литературы
        if total_students > 0:
            percent_accessible = min((total_literature * 6 / total_students) * 100, 100)
        else:
            percent_accessible = 0

        stats_list.append({
            "university": uni.name,
            "total_students": total_students,
            "total_directions": total_directions,
            "total_subjects": total_subjects,
            "total_literature": total_literature,
            "percent_accessible": round(percent_accessible, 2)
        })

    return stats_list
