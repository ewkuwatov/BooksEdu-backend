from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.direction import Direction
from app.models.subject import Subject
from app.schemas.subject import SubjectCreate, SubjectOut, SubjectUpdate
from app.dependencies import get_current_user

router = APIRouter(prefix="/subjects", tags=["subjects"])


# ---- Получение ----
@router.get("/", response_model=List[SubjectOut])
async def get_subjects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Subject).options(selectinload(Subject.directions))
    )
    subjects = result.scalars().unique().all()

    return [
        SubjectOut(
            id=s.id,
            name=s.name,
            kafedra_id=s.kafedra_id,
            university_id=s.university_id,
            direction_ids=[d.id for d in s.directions],
        )
        for s in subjects
    ]

@router.get("/university/{university_id}", response_model=List[SubjectOut])
async def get_subjects_by_university(
    university_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # 🔒 Ограничение по ролям
    if current_user.role == "superadmin" and university_id != current_user.university_id:
        raise HTTPException(status_code=403, detail="Not your university")
    if current_user.role not in ("owner", "superadmin"):
        raise HTTPException(status_code=403, detail="Not allowed")

    result = await db.execute(
        select(Subject)
        .options(selectinload(Subject.directions))
        .where(Subject.university_id == university_id)
    )
    subjects = result.scalars().unique().all()

    return [
        SubjectOut(
            id=s.id,
            name=s.name,
            kafedra_id=s.kafedra_id,
            university_id=s.university_id,
            direction_ids=[d.id for d in s.directions],
        )
        for s in subjects
    ]

# ---- Создание нескольких предметов ---- (owner / superadmin)
@router.post("/bulk", response_model=List[SubjectOut])
async def create_subjects_bulk(
    subjects: List[SubjectCreate],
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if len(subjects) > 10:
        raise HTTPException(status_code=400, detail="Limit is 10 subjects at once")

    created_subjects = []

    for item in subjects:
        if current_user.role == "superadmin":
            item.university_id = current_user.university_id
        elif current_user.role == "owner":
            if not item.university_id:
                raise HTTPException(
                    status_code=400,
                    detail="university_id is required for owner"
                )
        else:
            raise HTTPException(status_code=403, detail="Not allowed")

        # Проверка направлений
        result = await db.execute(
            select(Direction).where(
                Direction.id.in_(item.direction_ids),
                Direction.university_id == item.university_id
            )
        )
        directions = result.scalars().all()
        if len(directions) != len(item.direction_ids):
            raise HTTPException(
                status_code=404,
                detail=f"Some directions not found for {item.name} in university {item.university_id}"
            )

        # ✅ Проверка на уникальность (имя + кафедра + университет)
        existing = await db.execute(
            select(Subject).where(
                Subject.name == item.name,
                Subject.kafedra_id == item.kafedra_id,
                Subject.university_id == item.university_id
            )
        )
        if existing.scalars().first():
            raise HTTPException(
                status_code=400,
                detail=f"Subject '{item.name}' already exists in this kafedra and university"
            )

        subject = Subject(
            name=item.name,
            kafedra_id=item.kafedra_id,
            university_id=item.university_id,
            directions=directions
        )
        db.add(subject)
        created_subjects.append(subject)

    await db.commit()

    # ✅ подгружаем связи directions заново
    ids = [s.id for s in created_subjects]
    result = await db.execute(
        select(Subject)
        .options(selectinload(Subject.directions))
        .where(Subject.id.in_(ids))
    )
    subjects_with_dirs = result.scalars().unique().all()

    return [
        SubjectOut(
            id=s.id,
            name=s.name,
            kafedra_id=s.kafedra_id,
            university_id=s.university_id,
            direction_ids=[d.id for d in s.directions],
        )
        for s in subjects_with_dirs
    ]


# ---- Обновление ---- (owner / superadmin)
@router.put("/{subject_id}", response_model=SubjectOut)
async def update_subject(
    subject_id: int,
    data: SubjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    result = await db.execute(
        select(Subject)
        .options(selectinload(Subject.directions))
        .where(Subject.id == subject_id)
    )
    subject = result.scalars().first()

    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    if current_user.role == "superadmin" and subject.university_id != current_user.university_id:
        raise HTTPException(status_code=403, detail="Not your university")
    if current_user.role not in ("owner", "superadmin"):
        raise HTTPException(status_code=403, detail="Not allowed")

    update_data = data.model_dump(exclude_unset=True)

    # если direction_ids переданы — обновляем связи
    if "direction_ids" in update_data:
        result = await db.execute(
            select(Direction).where(
                Direction.id.in_(update_data["direction_ids"]),
                Direction.university_id == subject.university_id
            )
        )
        directions = result.scalars().all()
        if len(directions) != len(update_data["direction_ids"]):
            raise HTTPException(status_code=404, detail="Some directions not found")
        subject.directions = directions
        update_data.pop("direction_ids")

    # ✅ Проверка уникальности при изменении имени/кафедры/университета
    if any(f in update_data for f in ("name", "kafedra_id", "university_id")):
        new_name = update_data.get("name", subject.name)
        new_kafedra_id = update_data.get("kafedra_id", subject.kafedra_id)
        new_university_id = update_data.get("university_id", subject.university_id)

        existing = await db.execute(
            select(Subject).where(
                Subject.name == new_name,
                Subject.kafedra_id == new_kafedra_id,
                Subject.university_id == new_university_id,
                Subject.id != subject.id
            )
        )
        if existing.scalars().first():
            raise HTTPException(
                status_code=400,
                detail=f"Subject '{new_name}' already exists in this kafedra and university"
            )

    for field, value in update_data.items():
        setattr(subject, field, value)

    await db.commit()
    await db.refresh(subject)

    return SubjectOut(
        id=subject.id,
        name=subject.name,
        kafedra_id=subject.kafedra_id,
        university_id=subject.university_id,
        direction_ids=[d.id for d in subject.directions],
    )


# ---- Удаление ---- (owner / superadmin)
@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject(
    subject_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    subject = await db.get(Subject, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    if current_user.role == "superadmin" and subject.university_id != current_user.university_id:
        raise HTTPException(status_code=403, detail="Not your university")
    if current_user.role not in ("owner", "superadmin"):
        raise HTTPException(status_code=403, detail="Not allowed")

    await db.delete(subject)
    await db.commit()
    return None
