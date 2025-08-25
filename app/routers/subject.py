# app/routers/subject.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.direction import Direction
from app.models.subject import Subject
from app.schemas.subject import SubjectCreate, SubjectOut, SubjectUpdate
from app.dependencies import get_current_user

router = APIRouter(prefix="/subjects", tags=["subjects"])

@router.get("/", response_model=List[SubjectOut])
async def get_subjects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Subject))
    return result.scalars().all()

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

        existing = await db.execute(
            select(Subject).where(
                Subject.name == item.name,
                Subject.university_id == item.university_id
            )
        )
        if existing.scalars().first():
            raise HTTPException(
                status_code=400,
                detail=f"Subject with name '{item.name}' already exists in this university"
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
    for subject in created_subjects:
        await db.refresh(subject)

    return created_subjects


# ---- Обновление ---- (owner / superadmin)
@router.put("/{subject_id}", response_model=SubjectOut)
async def update_subject(
    subject_id: int,
    data: SubjectUpdate,
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

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(subject, field, value)

    await db.commit()
    await db.refresh(subject)
    return subject


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
